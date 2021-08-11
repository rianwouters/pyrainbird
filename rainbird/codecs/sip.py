from .base import CodecBase


class SipBase(CodecBase):
    def __init__(self, messages, child=None):
        super().__init__(child)
        self.messages = messages

    def get(self, id):
        msg = self.messages.get(id)
        if msg:
            return msg
        raise Exception(f"Unknown SIP message id ({id})")


class SipDecoder(SipBase):
    def __init__(self, messages, child=None):
        super().__init__(messages, child)

    def _code(self, data):
        id = int(data[:2], 16)
        tpl = self.get(id).get("template", {})
        return {"id": id} | {
            k: int(data[v[0] : v[1]], 16) for k, v in tpl.items() if v[1] <= len(data)
        }


class SipEncoder(SipBase):
    def __init__(self, messages, child=None):
        super().__init__(messages, child)

    def _code(self, data):
        id = data[0]
        msg = self.get(id)
        l = msg["length"]
        if len(data) != l:
            raise Exception(f"Expected {l - 1} parameters")
        params = list(map(lambda x: int(x), data))
        return ("{:02X}" * l).format(*params)
