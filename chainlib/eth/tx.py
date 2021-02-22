# standard imports
import logging

# third-party imports
import sha3
from hexathon import (
        strip_0x,
        add_0x,
        )
from eth_keys import KeyAPI
from eth_keys.backends import NativeECCBackend
from rlp import decode as rlp_decode
from rlp import encode as rlp_encode
from crypto_dev_signer.eth.transaction import EIP155Transaction


# local imports
from chainlib.hash import keccak256_hex_to_hex
from chainlib.status import Status
from .address import to_checksum
from .constant import (
        MINIMUM_FEE_UNITS,
        MINIMUM_FEE_PRICE,
        ZERO_ADDRESS,
        )
from .rpc import jsonrpc_template

logg = logging.getLogger(__name__)


field_debugs = [
        'nonce',
        'gasPrice',
        'gas',
        'to',
        'value',
        'data',
        'v',
        'r',
        's',
        ]

def unpack(tx_raw_bytes, chain_id=1):
    d = rlp_decode(tx_raw_bytes)

    logg.debug('decoding using chain id {}'.format(chain_id))
    j = 0
    for i in d:
        logg.debug('decoded {}: {}'.format(field_debugs[j], i.hex()))
        j += 1
    vb = chain_id
    if chain_id != 0:
        v = int.from_bytes(d[6], 'big')
        vb = v - (chain_id * 2) - 35
    s = b''.join([d[7], d[8], bytes([vb])])
    so = KeyAPI.Signature(signature_bytes=s)

    h = sha3.keccak_256()
    h.update(rlp_encode(d))
    signed_hash = h.digest()

    d[6] = chain_id
    d[7] = b''
    d[8] = b''

    h = sha3.keccak_256()
    h.update(rlp_encode(d))
    unsigned_hash = h.digest()
    
    p = so.recover_public_key_from_msg_hash(unsigned_hash)
    a = p.to_checksum_address()
    logg.debug('decoded recovery byte {}'.format(vb))
    logg.debug('decoded address {}'.format(a))
    logg.debug('decoded signed hash {}'.format(signed_hash.hex()))
    logg.debug('decoded unsigned hash {}'.format(unsigned_hash.hex()))

    to = d[3].hex() or None
    if to != None:
        to = to_checksum(to)

    return {
        'from': a,
        'nonce': int.from_bytes(d[0], 'big'),
        'gasPrice': int.from_bytes(d[1], 'big'),
        'gas': int.from_bytes(d[2], 'big'),
        'to': to, 
        'value': int.from_bytes(d[4], 'big'),
        'data': '0x' + d[5].hex(),
        'v': chain_id,
        'r': '0x' + s[:32].hex(),
        's': '0x' + s[32:64].hex(),
        'chainId': chain_id,
        'hash': '0x' + signed_hash.hex(),
        'hash_unsigned': '0x' + unsigned_hash.hex(),
            }


def receipt(hsh):
    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionReceipt'
    o['params'].append(add_0x(hsh))
    return o


class TxFactory:

    def __init__(self, signer=None, gas_oracle=None, nonce_oracle=None, chain_id=1):
        self.gas_oracle = gas_oracle
        self.nonce_oracle = nonce_oracle
        self.chain_id = chain_id
        self.signer = signer


    def build_raw(self, tx):
        txe = EIP155Transaction(tx, tx['nonce'], tx['chainId'])
        self.signer.signTransaction(txe)
        tx_raw = txe.rlp_serialize()
        tx_raw_hex = add_0x(tx_raw.hex())
        tx_hash_hex = add_0x(keccak256_hex_to_hex(tx_raw_hex))
        return (tx_hash_hex, tx_raw_hex)

    def build(self, tx):
        (tx_hash_hex, tx_raw_hex) = self.build_raw(tx) 

        o = jsonrpc_template()
        o['method'] = 'eth_sendRawTransaction'
        o['params'].append(tx_raw_hex)

        return (tx_hash_hex, o)


    def template(self, sender, recipient, use_nonce=False):
        gas_price = MINIMUM_FEE_PRICE
        gas_limit = MINIMUM_FEE_UNITS
        if self.gas_oracle != None:
            (gas_price, gas_limit) = self.gas_oracle.get()
        logg.debug('using gas price {} limit {}'.format(gas_price, gas_limit))
        nonce = 0
        o = {
                'from': sender,
                'to': recipient,
                'value': 0,
                'data': '0x',
                'gasPrice': gas_price,
                'gas': gas_limit,
                'chainId': self.chain_id,
                }
        if self.nonce_oracle != None and use_nonce:
            nonce = self.nonce_oracle.next()
            logg.debug('using nonce {} for address {}'.format(nonce, sender))
        o['nonce'] = nonce
        return o


    def normalize(self, tx):
        txe = EIP155Transaction(tx, tx['nonce'], tx['chainId'])
        txes = txe.serialize()
        return {
            'from': tx['from'],
            'to': txes['to'],
            'gasPrice': txes['gasPrice'],
            'gas': txes['gas'],
            'data': txes['data'],
                }


    def set_code(self, tx, data, update_fee=True):
        tx['data'] = data
        if update_fee:
            logg.debug('using hardcoded gas limit of 8000000 until we have reliable vm executor')
            tx['gas'] = 8000000
        return tx


class Tx:

    def __init__(self, src, block=None, rcpt=None):
        self.index = -1
        if block != None:
            self.index = int(strip_0x(src['transactionIndex']), 16)
        self.value = int(strip_0x(src['value']), 16)
        self.nonce = int(strip_0x(src['nonce']), 16)
        self.hash = strip_0x(src['hash'])
        address_from = strip_0x(src['from'])
        self.gasPrice = int(strip_0x(src['gasPrice']), 16)
        self.gasLimit = int(strip_0x(src['gas']), 16)
        self.outputs = [to_checksum(address_from)]

        inpt = src['input']
        if inpt != '0x':
            inpt = strip_0x(inpt)
        else:
            inpt = None
        self.payload = inpt

        to = src['to']
        if to == None:
            to = ZERO_ADDRESS
        self.inputs = [to_checksum(strip_0x(to))]

        self.block = block
        self.wire = src['raw']
        self.src = src

        self.status = Status.PENDING
        self.logs = None

        if rcpt != None:
            self.apply_receipt(rcpt)
   

    def apply_receipt(self, rcpt):
        if rcpt['status'] == 1:
            self.status = Status.SUCCESS
        elif rcpt['status'] == 0:
            self.status = Status.PENDING
        self.logs = rcpt['logs']


    def __repr__(self):
        return 'block {} tx {} {}'.format(self.block.number, self.index, self.hash)


    def __str__(self):
        return """from {}
to {}
value {}
nonce {}
gasPrice {}
gasLimit {}
input {}""".format(
        self.outputs[0],
        self.inputs[0],
        self.value,
        self.nonce,
        self.gasPrice,
        self.gasLimit,
        self.payload,
        )
