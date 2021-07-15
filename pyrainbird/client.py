from pyrainbird.jsonrpc_codec import JSONRPCEncoder

from .aes_codec import AESDecoder, AESEncoder
from .http_session import HTTPSession
from .jsonrpc_codec import JSONRPCDecoder, JSONRPCEncoder
from .sip_codec import SipDecoder, SipEncoder, TunnelSipDecoder, TunnelSipEncoder
from .sip_messages import messages


class RainbirdClient(HTTPSession):
    def __init__(self, password, **kwargs):
        super().__init__(**kwargs)
        self.encoder = SipEncoder(
            messages, TunnelSipEncoder(JSONRPCEncoder(AESEncoder(password)))
        )
        self.decoder = AESDecoder(
            password, JSONRPCDecoder(TunnelSipDecoder(SipDecoder(messages)))
        )
        self.headers.update(
            {
                "Accept-Language": "en",
                "User-Agent": "RainBird/2.0 CFNetwork/811.5.4 Darwin/16.7.0",
                "Content-Type": "application/octet-stream",
            }
        )

    def post(self, url, data, **kwargs):
        data = self.encoder(data)
        resp = super().post(url, data=data, **kwargs)
        return self.decoder(resp.content)
