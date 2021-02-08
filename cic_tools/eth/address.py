# third-party imports
import sha3
from hexathon import (
        strip_0x,
        uniform,
    )


def to_checksum(address_hex):
        address_hex = strip_0x(address_hex)
        address_hex = uniform(address_hex)
        h = sha3.keccak_256()
        h.update(address_hex.encode('utf-8'))
        z = h.digest()

        checksum_address_hex = '0x'

        for (i, c) in enumerate(address_hex):
            if c in '1234567890':
                checksum_address_hex += c
            elif c in 'abcdef':
                if z[int(i / 2)] & (0x80 >> ((i % 2) * 4)) > 1:
                    checksum_address_hex += c.upper()
                else:
                    checksum_address_hex += c

        return checksum_address_hex
