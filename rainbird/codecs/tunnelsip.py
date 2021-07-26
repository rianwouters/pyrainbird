from .base import CodecBase


class TunnelSipEncoder(CodecBase):
    def __init__(self, child=None):
        super().__init__(child)

    def _code(self, data):
        return {
            "method": "tunnelSip",
            "params": {"data": data, "length": len(data) // 2},
        }


class TunnelSipDecoder(CodecBase):
    def __init__(self, child=None):
        super().__init__(child)

    def _code(self, data):
        return data["data"]
