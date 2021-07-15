from .codec_base import CodecBase
from time import time
from json import loads, dumps


class JSONRPCEncoder(CodecBase):
    def __init__(self, parent=None, version="2.0"):
        super().__init__(parent)
        self.version = version

    def _code(self, data):
        return dumps(
            {
                "id": time(),
                "jsonrpc": self.version,
                "method": data["method"],
                "params": data["params"],
            }
        )


class JSONRPCDecoder(CodecBase):
    def __init__(self, parent=None):
        super().__init__(parent)

    def _code(self, data):
        d = loads(data)
        err = d.get("error")
        if err:
            raise Exception(f"JSONRPC error {err['code']}, {err['message']}")
        return d["result"]
