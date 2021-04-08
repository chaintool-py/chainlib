#!python3

"""Token balance query script

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import sys
import os
import json
import argparse
import logging

# third-party imports
from hexathon import (
        add_0x,
        strip_0x,
        even,
        )
import sha3
from eth_abi import encode_single

# local imports
from chainlib.eth.address import (
        to_checksum_address,
        is_checksum_address,
        )
from chainlib.jsonrpc import (
        jsonrpc_template,
        jsonrpc_result,
        )
from chainlib.eth.block import block_latest
from chainlib.eth.tx import count
from chainlib.eth.erc20 import ERC20
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.gas import (
        OverrideGasOracle,
        balance,
        price,
        )
from chainlib.chain import ChainSpec

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

default_abi_dir = os.environ.get('ETH_ABI_DIR', '/usr/share/local/cic/solidity/abi')
default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default=default_eth_provider, type=str, help='Web3 provider url (http only)')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-H', '--human', dest='human', action='store_true', help='Use human-friendly formatting')
argparser.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Auto-convert address to checksum adddress')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Include summary for keyfile')
argparser.add_argument('address', nargs='?', type=str, help='Include summary for address (conflicts with -y)')
args = argparser.parse_args()


if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

signer = None
holder_address = None
if args.address != None:
    if not args.u and is_checksum_address(args.address):
        raise ValueError('invalid checksum address {}'.format(args.address))
        holder_address = add_0x(args.address)
elif args.y != None:
    f = open(args.y, 'r')
    o = json.load(f)
    f.close()
    holder_address = add_0x(to_checksum_address(o['address']))


#if holder_address != None:
#    passphrase_env = 'ETH_PASSPHRASE'
#    if args.env_prefix != None:
#        passphrase_env = args.env_prefix + '_' + passphrase_env
#    passphrase = os.environ.get(passphrase_env)
#    logg.error('pass {}'.format(passphrase_env))
#    if passphrase == None:
#        logg.warning('no passphrase given')
#        passphrase=''
#
#    holder_address = None
#    keystore = DictKeystore()
#    if args.y != None:
#        logg.debug('loading keystore file {}'.format(args.y))
#        signer_address = keystore.import_keystore_file(args.y, password=passphrase)
#        logg.debug('now have key for signer address {}'.format(signer_address))
#    signer = EIP155Signer(keystore)

conn = EthHTTPConnection(args.p)
gas_oracle = OverrideGasOracle(conn)

token_symbol = 'eth'

chain_spec = ChainSpec.from_chain_str(args.i)

human = args.human


def main():
    o = block_latest()
    r = conn.do(o)
    n = int(r, 16)
    if human:
        n = format(n, ',')
    sys.stdout.write('Block: {}\n'.format(n))

    o = price()
    r = conn.do(o)
    n = int(r, 16)
    if human:
        n = format(n, ',')
    sys.stdout.write('Gasprice: {}\n'.format(n))

    if holder_address != None:
        o = count(holder_address)
        r = conn.do(o)
        n = int(r, 16)
        sys.stdout.write('Address: {}\n'.format(holder_address))
        sys.stdout.write('Nonce: {}\n'.format(n))


if __name__ == '__main__':
    main()
