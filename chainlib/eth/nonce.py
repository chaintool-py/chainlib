# third-party imports
from hexathon import (
        add_0x,
        strip_0x,
        )

# local imports
from chainlib.eth.rpc import jsonrpc_template


def nonce(address):
    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionCount'
    o['params'].append(address)
    o['params'].append('pending')
    return o


class DefaultNonceOracle:

    def __init__(self, address, conn):
        self.address = address
        self.conn = conn


    def next(self):
        o = nonce(self.address)
        r = self.conn.do(o)
        n = strip_0x(r)
        return int(n, 16)
