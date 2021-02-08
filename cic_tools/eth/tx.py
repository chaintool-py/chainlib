# standard imports
import logging

# third-party imports
import sha3
from eth_keys import KeyAPI
from eth_keys.backends import NativeECCBackend
from rlp import decode as rlp_decode
from rlp import encode as rlp_encode

# local imports
from .address import to_checksum

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

def unpack_signed(tx_raw_bytes, chain_id=1):
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


