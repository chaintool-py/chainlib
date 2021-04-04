# local imports
from chainlib.eth.tx import unpack
from hexathon import (
        strip_0x,
        add_0x,
        )

def decode_for_puny_humans(tx_raw, chain_spec, writer):
    tx_raw = strip_0x(tx_raw)
    tx_raw_bytes = bytes.fromhex(tx_raw)
    tx = unpack(tx_raw_bytes, chain_spec)
    for k in tx.keys():
        x = None
        if k == 'value':
            x = '{:.18f} eth'.format(tx[k] / (10**18))
        elif k == 'gasPrice':
            x = '{} gwei'.format(int(tx[k] / (10**9)))
        if x != None:
            writer.write('{}: {} ({})\n'.format(k, tx[k], x))
        else:
            writer.write('{}: {}\n'.format(k, tx[k]))
    writer.write('src: {}\n'.format(add_0x(tx_raw)))
