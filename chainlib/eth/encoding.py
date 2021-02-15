from eth_abi import (
        encode_single as __encode_single,
        decode_single as __decode_single,
        )

def abi_encode(signature, *args):
    return __encode_single(signature, *args)


def abi_encode_hex(signature, *args):
    return __encode_single(signature, *args).hex()


def abi_decode(signature, *args):
    return __decode_single(signature, *args)


def abi_decode_hex(signature, *args):
    return __decode_single(signature, *args).hex()

