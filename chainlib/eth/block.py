# third-party imports
from chainlib.jsonrpc import jsonrpc_template
from chainlib.eth.tx import Tx
from hexathon import (
        add_0x,
        strip_0x,
        even,
        )


def block_latest():
    o = jsonrpc_template()
    o['method'] = 'eth_blockNumber'
    return o


def block_by_hash(hsh, include_tx=True):
    o = jsonrpc_template()
    o['method'] = 'eth_getBlockByHash'
    o['params'].append(hsh)
    o['params'].append(include_tx)
    return o


def block_by_number(n, include_tx=True):
    nhx = add_0x(even(hex(n)[2:]))
    o = jsonrpc_template()
    o['method'] = 'eth_getBlockByNumber'
    o['params'].append(nhx)
    o['params'].append(include_tx)
    return o


def transaction_count(block_hash):
    o = jsonrpc_template()
    o['method'] = 'eth_getBlockTransactionCountByHash'
    o['params'].append(block_hash)
    return o


class Block:
    
    def __init__(self, src):
        self.hash = src['hash']
        self.number = int(strip_0x(src['number']), 16)
        self.txs = src['transactions']
        self.block_src = src
        self.timestamp = int(strip_0x(src['timestamp']), 16)


    def src(self):
        return self.block_src


    def tx(self, i):
        return Tx(self.txs[i], self)


    def tx_src(self, i):
        return self.txs[i]


    def __str__(self):
        return 'block {} {} ({} txs)'.format(self.number, self.hash, len(self.txs))
