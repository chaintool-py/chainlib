# third-party imports
from hexathon import (
        add_0x,
        strip_0x,
        )
from crypto_dev_signer.eth.transaction import EIP155Transaction

# local imports
from chainlib.eth.rpc import jsonrpc_template
from chainlib.eth.tx import TxFactory
from chainlib.eth.hash import keccak256_hex_to_hex


def price():
    o = jsonrpc_template()
    o['method'] = 'eth_gasPrice'
    return o


def balance(address):
    o = jsonrpc_template()
    o['method'] = 'eth_getBalance'
    o['params'].append(address)
    return o


class GasTxFactory(TxFactory):

    def create(self, sender, recipient, value):
        tx = self.template(sender, recipient)
        tx['value'] = value
        txe = EIP155Transaction(tx, tx['nonce'], tx['chainId'])
        self.signer.signTransaction(txe)
        tx_raw = txe.rlp_serialize()
        tx_raw_hex = add_0x(tx_raw.hex())
        tx_hash_hex = add_0x(keccak256_hex_to_hex(tx_raw_hex))

        o = jsonrpc_template()
        o['method'] = 'eth_sendRawTransaction'
        o['params'].append(tx_raw_hex)

        return (tx_hash_hex, o)


class DefaultGasOracle:

    def __init__(self, conn):
        self.conn = conn


    def get(self):
        o = price()
        r = self.conn.do(o)
        n = strip_0x(r)
        return int(n, 16)
