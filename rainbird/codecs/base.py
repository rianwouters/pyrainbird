from logging import getLogger

class CodecBase:
    def __init__(self, child):
        self.child = child
        self.logger = getLogger(self.__class__.__name__)

    def __call__(self, data): 
        coded = self._code(data)
        return self.child(coded) if self.child else coded 
