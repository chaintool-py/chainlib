class NonceOracle:

    def __init__(self, address, id_generator=None, confirmed=False):
        self.address = address
        self.nonce = self.get_nonce(confirmed=confirmed)


    def get_nonce(self):
        raise NotImplementedError()


    def next_nonce(self):
        raise NotImplementedError()
