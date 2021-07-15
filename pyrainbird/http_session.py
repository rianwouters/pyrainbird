from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from logging import getLogger


class HTTPSession(Session):
    def __init__(
        self,
        retry_strategy=Retry(3, backoff_factor=20),
        logger=getLogger(__name__),
    ):
        super().__init__()
        self.logger = logger
        self.mount("http://", HTTPAdapter(max_retries=retry_strategy))

    def request(self, method, url, **kwargs):
        resp = super().request(method, url, **kwargs)

        if resp is None:
            raise Exception("No response returned.")

        if resp.status_code != 200:
            raise Exception(f"HTTP error: {resp.status_code}, {resp.reason}")

        return resp
