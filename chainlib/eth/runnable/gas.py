#!python3

"""Gas transfer script

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
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.keystore import DictKeystore
from hexathon import (
        add_0x,
        strip_0x,
        )

# local imports
from chainlib.eth.address import to_checksum
from chainlib.eth.connection import HTTPConnection
from chainlib.eth.rpc import jsonrpc_template
from chainlib.eth.nonce import DefaultNonceOracle
from chainlib.eth.gas import (
        DefaultGasOracle,
        GasTxFactory,
        )
from chainlib.eth.gas import balance as gas_balance

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()


default_abi_dir = '/usr/share/local/cic/solidity/abi'
default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
argparser.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='Ethereum:1', help='Chain specification string')
argparser.add_argument('-a', '--signer-address', dest='a', type=str, help='Signing address')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Auto-convert address to checksum adddress')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('recipient', type=str, help='Ethereum address of recipient')
argparser.add_argument('amount', type=int, help='Amount of tokens to mint and gift')
args = argparser.parse_args()


if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

block_all = args.ww
block_last = args.w or block_all

signer_address = None
keystore = DictKeystore()
if args.y != None:
    logg.debug('loading keystore file {}'.format(args.y))
    signer_address = keystore.import_keystore_file(args.y)
    logg.debug('now have key for signer address {}'.format(signer_address))
signer = EIP155Signer(keystore)

conn = HTTPConnection(args.p)
nonce_oracle = DefaultNonceOracle(signer_address, conn)
gas_oracle = DefaultGasOracle(conn)

chain_pair = args.i.split(':')
chain_id = int(chain_pair[1])

value = args.amount

g = GasTxFactory(signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle, chain_id=chain_id)


def balance(address):
    o = gas_balance(address)
    r = conn.do(o)
    hx = strip_0x(r)
    return int(hx, 16)


def main():
    recipient = to_checksum(args.recipient)
    if not args.u and recipient != add_0x(args.recipient):
        raise ValueError('invalid checksum address')

    logg.info('gas transfer from {} to {} value {}'.format(signer_address, recipient, value))
    logg.debug('sender {} balance before: {}'.format(signer_address, balance(signer_address)))
    logg.debug('recipient {} balance before: {}'.format(recipient, balance(recipient)))
 
    (tx_hash_hex, o) = g.create(signer_address, recipient, value)
    conn.do(o)

    if block_last:
        conn.wait(tx_hash_hex)
        logg.debug('sender {} balance after: {}'.format(signer_address, balance(signer_address)))
        logg.debug('recipient {} balance after: {}'.format(recipient, balance(recipient)))
 

    print(tx_hash_hex)


if __name__ == '__main__':
    main()