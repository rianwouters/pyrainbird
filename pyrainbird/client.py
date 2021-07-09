import json
import logging
from time import time

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .encryption import encrypt, decrypt

headers = {
    "Accept-Language": "en",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "RainBird/2.0 CFNetwork/811.5.4 Darwin/16.7.0",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Content-Type": "application/octet-stream",
}

def jsonrpc(data, length, id = time()): 
    id = time()
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
        retry_strategy=Retry(3, backoff_factor=20),
        logger=logging.getLogger(__name__),
    ):
        self.host = host
        self.password = password
        self.logger = logger
        self.session = Session()
        self.session.mount("http://", HTTPAdapter(max_retries=retry_strategy))


    def request(self, data, length):
        msg = jsonrpc(data, length)
        self.logger.debug(
            f"Sending {msg} to {self.host}"
        )
        try:
            resp = self.session.post(
                f"http://{self.host}/stick",
                encrypt(msg, self.password),
                headers=headers,
                timeout=20,
            )

            if resp is None:
                raise Exception("No response returned.")

            if resp.status_code != 200:
                raise Exception(f"Response: {resp.status_code}, {resp.reason}")
            
            decrypted_data = (
                decrypt(resp.content, self.password)
                .decode("UTF-8")
                .rstrip("\x10")
                .rstrip("\x0A")
                .rstrip("\x00")
                .rstrip()
            )
            self.logger.debug(f"Response: {decrypted_data}")
            return json.loads(decrypted_data)["result"]["data"]

        except Exception as e:
            raise Exception(f"Unable to connect: {e}")

