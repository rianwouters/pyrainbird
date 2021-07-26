from .base import CodecBase
from time import time
from json import loads, dumps


class JSONRPCEncoder(CodecBase):
    def __init__(self, parent=None, version="2.0"):
        super().__init__(parent)
        self.version = version

    def _code(self, method, params=None, id=time()):
        if isinstance(method, dict):
            method,params, id = method["method"], method["params"], method.get("id", id)
        r = dumps(
            {
                "id": id,
                "jsonrpc": self.version,
                "method": method,
                "params": params,
            }
        )
        self.logger.debug(r)
        return r


class JSONRPCDecoder(CodecBase):
    def __init__(self, parent=None):
        super().__init__(parent)

    def _code(self, data):
        d = loads(data)
        self.logger.debug(d)
        err = d.get("error")
        if err:
            raise Exception(f"JSONRPC error {err['code']}, {err['message']}")
        return d["result"]
