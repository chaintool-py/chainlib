import sha3


def keccak256_hex(s):
    h = sha3.keccak_256()
    h.update(s.encode('utf-8'))
    return h.digest().hex()
