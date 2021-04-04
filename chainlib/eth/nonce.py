# third-party imports
from hexathon import (
        add_0x,
        strip_0x,
        )

# local imports
from chainlib.jsonrpc import jsonrpc_template


def nonce(address):
    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionCount'
    o['params'].append(address)
    o['params'].append('pending')
    return o


class NonceOracle:

    def __init__(self, address):
        self.address = address
        self.nonce = self.get_nonce()


    def get_nonce(self):
        raise NotImplementedError('Class must be extended')


    def next_nonce(self):
        n = self.nonce
        self.nonce += 1
        return n


class RPCNonceOracle(NonceOracle):

    def __init__(self, address, conn):
        self.conn = conn
        super(RPCNonceOracle, self).__init__(address)


    def get_nonce(self):
        o = nonce(self.address)
        r = self.conn.do(o)
        n = strip_0x(r)
        return int(n, 16)


class OverrideNonceOracle(NonceOracle):


    def __init__(self, address, nonce):
        self.nonce = nonce
        super(OverrideNonceOracle, self).__init__(address)


    def get_nonce(self):
        return self.nonce


DefaultNonceOracle = RPCNonceOracle
