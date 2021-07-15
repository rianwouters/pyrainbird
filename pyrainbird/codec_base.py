class CodecBase:
    def __init__(self, child=None):
        self.child = child

    def __call__(self, data): 
        coded = self._code(data)
        return self.child(coded) if self.child else coded 
