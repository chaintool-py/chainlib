class NonceOracle:

    def __init__(self, address, confirmed=True):
        self.address = address
        self.nonce = self.get_nonce()
        self.confirmed = confirmed


    def get_nonce(self):
        raise NotImplementedError()


    def next_nonce(self):
        raise NotImplementedError()
