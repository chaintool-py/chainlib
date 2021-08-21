# external imports
import sha3
from hexathon import strip_0x


def keccak256_hex(s):
    """Hex representation of Keccak256 hash of utf-8 string content.

    :param s: utf-8 string to hash
    :type s: str
    :rtype: str
    :returns: Hex-value of keccak256 hash
    """
    h = sha3.keccak_256()
    h.update(s.encode('utf-8'))
    return h.digest().hex()


def keccak256_string_to_hex(s):
    """Alias of keccak256_hex
    """
    return keccak256_hex(s)


def keecak256_bytes_to_hex(b):
    """Hex representation of Keccak256 hash of literal byte content.
    
    :param b: bytes to hash
    :type b: bytes
    :rtype: str
    :returns: Hex-value of keccak256 hash
    """
    h = sha3.keccak_256()
    h.update(b)
    return h.digest().hex()


def keccak256_hex_to_hex(hx):
    """Hex representation of Keccak256 hash of byte value of hex content.

    :param hx: Hex-value of bytes to hash
    :type hx: str
    :rtype: str
    :returns: Hex-value of keccak256 hash
    """
    h = sha3.keccak_256()
    b = bytes.fromhex(strip_0x(hx))
    h.update(b)
    return h.digest().hex()
