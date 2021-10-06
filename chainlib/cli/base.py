# standard imports
import enum
import os

script_dir = os.path.dirname(os.path.realpath(__file__))

default_config_dir = os.path.join(script_dir, '..', 'data', 'config')


# powers of two
class Flag(enum.IntEnum):
    # read - nibble 1-2
    VERBOSE = 1
    CONFIG = 2
    RAW = 4
    ENV_PREFIX = 8
    PROVIDER = 16
    CHAIN_SPEC = 32
    UNSAFE = 64
    SEQ = 128
    # read/write - nibble 3
    KEY_FILE = 256
    FEE = 512 # this must be defined separately now since some rpcs demand minimum base fee price
    NONCE = 1024
    # write - nibble 4
    SIGN = 4096
    NO_TARGET = 8192
    EXEC = 16384
    WALLET = 32768
    # network - nibble 5
    WAIT = 65536
    WAIT_ALL = 131072
    SEND = 262144
    # rpc extras - nibble 6
    RPC_AUTH = 1048576

argflag_std_read = 0x23ff 
argflag_std_write = 0xff31ff
argflag_std_base = 0x200f
argflag_std_target = 0x00e000
argflag_all = 0xffffff

def reset(flags, v):
    mask = ~(argflag_all & v)
    r = flags & mask
    return r
