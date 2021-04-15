# standard imports
import logging
import enum
import re

# external imports
import coincurve
import sha3
from hexathon import (
        strip_0x,
        add_0x,
        )
from rlp import decode as rlp_decode
from rlp import encode as rlp_encode
from crypto_dev_signer.eth.transaction import EIP155Transaction
from crypto_dev_signer.encoding import public_key_to_address
from potaahto.symbols import snake_and_camel


# local imports
from chainlib.hash import keccak256_hex_to_hex
from chainlib.status import Status
from .address import to_checksum
from .constant import (
        MINIMUM_FEE_UNITS,
        MINIMUM_FEE_PRICE,
        ZERO_ADDRESS,
        )
from chainlib.jsonrpc import jsonrpc_template

logg = logging.getLogger().getChild(__name__)



class TxFormat(enum.IntEnum):
    DICT = 0x00
    RAW = 0x01
    RAW_SIGNED = 0x02
    RAW_ARGS = 0x03
    RLP = 0x10
    RLP_SIGNED = 0x11
    JSONRPC = 0x10
     

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

def count(address, confirmed=False):
    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionCount'
    o['params'].append(address)
    if confirmed:
        o['params'].append('latest')
    else:
        o['params'].append('pending')
    return o

count_pending = count

def count_confirmed(address):
    return count(address, True)


def unpack(tx_raw_bytes, chain_spec):
    chain_id = chain_spec.chain_id()
    tx = __unpack_raw(tx_raw_bytes, chain_id)
    tx['nonce'] = int.from_bytes(tx['nonce'], 'big')
    tx['gasPrice'] = int.from_bytes(tx['gasPrice'], 'big')
    tx['gas'] = int.from_bytes(tx['gas'], 'big')
    tx['value'] = int.from_bytes(tx['value'], 'big')
    return tx


def unpack_hex(tx_raw_bytes, chain_spec):
    chain_id = chain_spec.chain_id()
    tx = __unpack_raw(tx_raw_bytes, chain_id)
    tx['nonce'] = add_0x(hex(tx['nonce']))
    tx['gasPrice'] = add_0x(hex(tx['gasPrice']))
    tx['gas'] = add_0x(hex(tx['gas']))
    tx['value'] = add_0x(hex(tx['value']))
    tx['chainId'] = add_0x(hex(tx['chainId']))
    return tx


def __unpack_raw(tx_raw_bytes, chain_id=1):
    d = rlp_decode(tx_raw_bytes)

    logg.debug('decoding using chain id {}'.format(str(chain_id)))
    
    j = 0
    for i in d:
        v = i.hex()
        if j != 3 and v == '':
            v = '00'
        logg.debug('decoded {}: {}'.format(field_debugs[j], v))
        j += 1
    vb = chain_id
    if chain_id != 0:
        v = int.from_bytes(d[6], 'big')
        vb = v - (chain_id * 2) - 35
    r = bytearray(32)
    r[32-len(d[7]):] = d[7]
    s = bytearray(32)
    s[32-len(d[8]):] = d[8]
    sig = b''.join([r, s, bytes([vb])])
    #so = KeyAPI.Signature(signature_bytes=sig)

    h = sha3.keccak_256()
    h.update(rlp_encode(d))
    signed_hash = h.digest()

    d[6] = chain_id
    d[7] = b''
    d[8] = b''

    h = sha3.keccak_256()
    h.update(rlp_encode(d))
    unsigned_hash = h.digest()
    
    #p = so.recover_public_key_from_msg_hash(unsigned_hash)
    #a = p.to_checksum_address()
    pubk = coincurve.PublicKey.from_signature_and_message(sig, unsigned_hash, hasher=None)
    a = public_key_to_address(pubk)
    logg.debug('decoded recovery byte {}'.format(vb))
    logg.debug('decoded address {}'.format(a))
    logg.debug('decoded signed hash {}'.format(signed_hash.hex()))
    logg.debug('decoded unsigned hash {}'.format(unsigned_hash.hex()))

    to = d[3].hex() or None
    if to != None:
        to = to_checksum(to)

    data = d[5].hex()
    try:
        data = add_0x(data)
    except:
        data = '0x'

    return {
        'from': a,
        'to': to, 
        'nonce': d[0],
        'gasPrice': d[1],
        'gas': d[2],
        'value': d[4],
        'data': data,
        'v': chain_id,
        'r': add_0x(sig[:32].hex()),
        's': add_0x(sig[32:64].hex()),
        'chainId': chain_id,
        'hash': add_0x(signed_hash.hex()),
        'hash_unsigned': add_0x(unsigned_hash.hex()),
            }


def transaction(hsh):
    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionByHash'
    o['params'].append(add_0x(hsh))
    return o

def transaction_by_block(hsh, idx):
    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionByBlockHashAndIndex'
    o['params'].append(add_0x(hsh))
    o['params'].append(hex(idx))
    return o


def receipt(hsh):
    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionReceipt'
    o['params'].append(add_0x(hsh))
    return o


def raw(tx_raw_hex):
    o = jsonrpc_template()
    o['method'] = 'eth_sendRawTransaction'
    o['params'].append(tx_raw_hex)
    return o


class TxFactory:

    fee = 8000000

    def __init__(self, chain_spec, signer=None, gas_oracle=None, nonce_oracle=None):
        self.gas_oracle = gas_oracle
        self.nonce_oracle = nonce_oracle
        self.chain_spec = chain_spec
        self.signer = signer


    def build_raw(self, tx):
        if tx['to'] == None or tx['to'] == '':
            tx['to'] = '0x'
        txe = EIP155Transaction(tx, tx['nonce'], tx['chainId'])
        tx_raw = self.signer.sign_transaction_to_rlp(txe)
        tx_raw_hex = add_0x(tx_raw.hex())
        tx_hash_hex = add_0x(keccak256_hex_to_hex(tx_raw_hex))
        return (tx_hash_hex, tx_raw_hex)


    def build(self, tx):
        (tx_hash_hex, tx_raw_hex) = self.build_raw(tx) 
        o = raw(tx_raw_hex)
        return (tx_hash_hex, o)


    def template(self, sender, recipient, use_nonce=False):
        gas_price = MINIMUM_FEE_PRICE
        gas_limit = MINIMUM_FEE_UNITS
        if self.gas_oracle != None:
            (gas_price, gas_limit) = self.gas_oracle.get_gas()
        logg.debug('using gas price {} limit {}'.format(gas_price, gas_limit))
        nonce = 0
        o = {
                'from': sender,
                'to': recipient,
                'value': 0,
                'data': '0x',
                'gasPrice': gas_price,
                'gas': gas_limit,
                'chainId': self.chain_spec.chain_id(),
                }
        if self.nonce_oracle != None and use_nonce:
            nonce = self.nonce_oracle.next_nonce()
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


    def finalize(self, tx, tx_format=TxFormat.JSONRPC):
        if tx_format == TxFormat.JSONRPC:
            return self.build(tx)
        elif tx_format == TxFormat.RLP_SIGNED:
            return self.build_raw(tx)
        raise NotImplementedError('tx formatting {} not implemented'.format(tx_format))


    def set_code(self, tx, data, update_fee=True):
        tx['data'] = data
        if update_fee:
            tx['gas'] = TxFactory.fee
            if self.gas_oracle != None:
                (price, tx['gas']) = self.gas_oracle.get_gas(code=data)
            else:
                logg.debug('using hardcoded gas limit of 8000000 until we have reliable vm executor')
        return tx


class Tx:

    # TODO: force tx type schema parser (whether expect hex or int etc)
    def __init__(self, src, block=None, rcpt=None):
        logg.debug('src {}'.format(src))
        self.src = self.src_normalize(src)
        self.index = -1
        tx_hash = add_0x(src['hash'])
        if block != None:
            i = 0
            for tx in block.txs:
                tx_hash_block = None
                try:
                    tx_hash_block = tx['hash']
                except TypeError:
                    tx_hash_block = add_0x(tx)
                logg.debug('tx {} cmp {}'.format(tx, tx_hash))
                if tx_hash_block == tx_hash:
                    self.index = i
                    break
                i += 1
            if self.index == -1:
                raise AttributeError('tx {} not found in block {}'.format(tx_hash, block.hash))
        self.block = block
        self.hash = strip_0x(tx_hash)
        try:
            self.value = int(strip_0x(src['value']), 16)
        except TypeError:
            self.value = int(src['value'])
        try:
            self.nonce = int(strip_0x(src['nonce']), 16)
        except TypeError:
            self.nonce = int(src['nonce'])
        address_from = strip_0x(src['from'])
        try:
            self.gas_price = int(strip_0x(src['gasPrice']), 16)
        except TypeError:
            self.gas_price = int(src['gasPrice'])
        try:
            self.gas_limit = int(strip_0x(src['gas']), 16)
        except TypeError:
            self.gas_limit = int(src['gas'])
        self.outputs = [to_checksum(address_from)]
        self.contract = None

        try:
            inpt = src['input']
        except KeyError:
            inpt = src['data']

        if inpt != '0x':
            inpt = strip_0x(inpt)
        else:
            inpt = ''
        self.payload = inpt

        to = src['to']
        if to == None:
            to = ZERO_ADDRESS
        self.inputs = [to_checksum(strip_0x(to))]

        self.block = block
        try:
            self.wire = src['raw']
        except KeyError:
            logg.warning('no inline raw tx src, and no raw rendering implemented, field will be "None"')

        self.src = src

        self.status = Status.PENDING
        self.logs = None

        if rcpt != None:
            self.apply_receipt(rcpt)
  
    
    @classmethod
    def src_normalize(self, src):
        return snake_and_camel(src) 


    def apply_receipt(self, rcpt):
        logg.debug('rcpt {}'.format(rcpt))
        try:
            status_number = int(rcpt['status'], 16)
        except TypeError:
            status_number = int(rcpt['status'])
        if status_number == 1:
            self.status = Status.SUCCESS
        elif status_number == 0:
            self.status = Status.ERROR
        # TODO: replace with rpc receipt/transaction translator when available
        contract_address = rcpt.get('contractAddress')
        if contract_address == None:
            contract_address = rcpt.get('contract_address')
        if contract_address != None:
            self.contract = contract_address
        self.logs = rcpt['logs']
        try:
            self.gas_used = int(rcpt['gasUsed'], 16)
        except TypeError:
            self.gas_used = int(rcpt['gasUsed'])


    def __repr__(self):
        return 'block {} tx {} {}'.format(self.block.number, self.index, self.hash)


    def __str__(self):
        s = """hash {}
from {}
to {}
value {}
nonce {}
gasPrice {}
gasLimit {}
input {}
""".format(
        self.hash,
        self.outputs[0],
        self.inputs[0],
        self.value,
        self.nonce,
        self.gas_price,
        self.gas_limit,
        self.payload,
        )

        if self.status != Status.PENDING:
            s += """gasUsed {}
""".format(
        self.gas_used,
        )

        s += 'status ' + self.status.name + '\n'

        if self.contract != None:
            s += """contract {}
""".format(
        self.contract,
        )
        return s

