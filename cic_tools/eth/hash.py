# third-party imports
import sha3
from hexathon import (
        add_0x,
        strip_0x,
        )


def keccak256_hex(s):
    h = sha3.keccak_256()
    h.update(s.encode('utf-8'))
    return h.digest().hex()


def keccak256_string_to_hex(s):
    return keccak256_hex(s)


def keecak256_bytes_to_hex(b):
    h = sha3.keccak_256()
    h.update(b)
    return h.digest().hex()


def keccak256_hex_to_hex(hx):
    h = sha3.keccak_256()
    b = bytes.fromhex(strip_0x(hx))
    h.update(b)
    return h.digest().hex()
