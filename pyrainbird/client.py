import json
import logging
from time import time, sleep

import requests

from .encryption import encrypt, decrypt

HEAD = {
    "Accept-Language": "en",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "RainBird/2.0 CFNetwork/811.5.4 Darwin/16.7.0",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Content-Type": "application/octet-stream",
}

def jsonrpc(id, data, length):    
    return json.dumps({
        "id": id,
        "jsonrpc":"2.0",
        "method":"tunnelSip",
        "params": {
            "data": data,
            "length": length
        }
    })

class RainbirdClient:
    def __init__(
        self,
        host,
        password,
        retry=3,
        retry_sleep=10,
        logger=logging.getLogger(__name__),
    ):
        self.host = host
        self.password = password
        self.retry = retry
        self.retry_sleep = retry_sleep
        self.logger = logger

    def request(self, data, length):
        msg = jsonrpc(time(), data, length)
        for i in range(0, self.retry):
            self.logger.debug(
                f"Sending {msg} to {self.host}, {i + 1}. try."
            )
            try:
                resp = requests.post(
                    f"http://{self.host}/stick",
                    encrypt(msg, self.password),
                    headers=HEAD,
                    timeout=20,
                )
            except Exception as e:
                self.logger.warning("Unable to connect: %s" % e)
                resp = None

            if resp is None:
                self.logger.warning("Response not returned.")
            elif resp.status_code != 200:
                self.logger.warning(
                    "Response: %d, %s" % (resp.status_code, resp.reason)
                )
            else:
                decrypted_data = (
                    decrypt(resp.content, self.password)
                    .decode("UTF-8")
                    .rstrip("\x10")
                    .rstrip("\x0A")
                    .rstrip("\x00")
                    .rstrip()
                )
                self.logger.debug("Response: %s" % decrypted_data)
                return json.loads(decrypted_data)["result"]["data"]
            sleep(self.retry_sleep)
            continue
