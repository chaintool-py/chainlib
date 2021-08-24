class NonceOracle:

    def __init__(self, address):
        self.address = address
        self.nonce = self.get_nonce()


    def get_nonce(self):
        raise NotImplementedError()


    def next_nonce(self):
        raise NotImplementedError()
