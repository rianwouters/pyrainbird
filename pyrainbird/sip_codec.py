from pyrainbird.codec_base import CodecBase


class SipBase(CodecBase):
    def __init__(self, messages, child=None):
        super().__init__(child)
        self.messages = messages

    def get(self, id):
        msg = self.messages.get(id)
        if not msg:
            raise Exception(f"Unknown SIP message id ({id})")
        return msg


class SipDecoder(SipBase):
    def __init__(self, messages, child=None):
        super().__init__(messages, child)

    def _code(self, data):
        id = int(data[:2], 16)
        tpl = self.get(id).get("template", {})
        return {k: int(data[v[0] : v[1]], 16) for k, v in tpl.items()}


class SipEncoder(SipBase):
    def __init__(self, messages, child=None):
        super().__init__(messages, child)

    def _code(self, data):
        id = int(data[0])
        msg = self.get(id)
        l = msg["length"]
        if len(data) != l:
            raise Exception(f"Expected {l - 1} parameters")
        params = list(map(lambda x: int(x), data))
        return ("{:02X}" * l).format(*params)


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
