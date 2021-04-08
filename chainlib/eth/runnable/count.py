# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import sys
import os
import json
import argparse
import logging

# local imports
from chainlib.eth.address import to_checksum
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.tx import count
from chainlib.chain import ChainSpec
from crypto_dev_signer.keystore.dict import DictKeystore
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('--env-prefix', default=os.environ.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
argparser.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Auto-convert address to checksum adddress')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('address', type=str, help='Ethereum address of recipient')
args = argparser.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)


signer_address = None
keystore = DictKeystore()
if args.y != None:
    logg.debug('loading keystore file {}'.format(args.y))
    signer_address = keystore.import_keystore_file(args.y, passphrase)
    logg.debug('now have key for signer address {}'.format(signer_address))
signer = EIP155Signer(keystore)

rpc = EthHTTPConnection(args.p)

def main():
    recipient = to_checksum(args.address)
    if not args.u and recipient != add_0x(args.address):
        raise ValueError('invalid checksum address')

    o = count(args.address)
    print(rpc.do(o))


if __name__ == '__main__':
    main()
