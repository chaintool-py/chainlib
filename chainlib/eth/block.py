from chainlib.eth.rpc import jsonrpc_template


def block(self):
    o = jsonrpc_template()
    o['method'] = 'eth_blockNumber'
    return o


def block_by_hash(self, hsh):
    o = jsonrpc_template()
    o['method'] = 'eth_getBlock'
    o['params'].append(hsh)
    return o


def block_by_number(self, n):
    o = jsonrpc_template()
    o['method'] = 'eth_getBlock'
    o['params'].append(n)
    return o
