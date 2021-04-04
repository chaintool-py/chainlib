#!python3

"""Gas transfer script

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import io
import sys
import os
import json
import argparse
import logging

# third-party imports
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.keystore.dict import DictKeystore
from hexathon import (
        add_0x,
        strip_0x,
        )

# local imports
from chainlib.eth.address import to_checksum
from chainlib.eth.connection import EthHTTPConnection
from chainlib.jsonrpc import jsonrpc_template
from chainlib.eth.nonce import (
        RPCNonceOracle,
        OverrideNonceOracle,
        )
from chainlib.eth.gas import (
        RPCGasOracle,
        OverrideGasOracle,
        Gas,
        )
from chainlib.eth.gas import balance as gas_balance
from chainlib.chain import ChainSpec
from chainlib.eth.runnable.util import decode_for_puny_humans

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()


default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
argparser.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('--env-prefix', default=os.environ.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
argparser.add_argument('--nonce', type=int, help='override nonce')
argparser.add_argument('--price', type=int, help='override gas price')
argparser.add_argument('--gas', type=int, help='override gas limit')
argparser.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Auto-convert address to checksum adddress')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('-s', '--send', dest='s', action='store_true', help='Send to network')
argparser.add_argument('recipient', type=str, help='Ethereum address of recipient')
argparser.add_argument('amount', type=int, help='Amount of tokens to mint and gift')
args = argparser.parse_args()


if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

block_all = args.ww
block_last = args.w or block_all

passphrase_env = 'ETH_PASSPHRASE'
if args.env_prefix != None:
    passphrase_env = args.env_prefix + '_' + passphrase_env
passphrase = os.environ.get(passphrase_env)
if passphrase == None:
    logg.warning('no passphrase given')
    passphrase=''

signer_address = None
keystore = DictKeystore()
if args.y != None:
    logg.debug('loading keystore file {}'.format(args.y))
    signer_address = keystore.import_keystore_file(args.y, password=passphrase)
    logg.debug('now have key for signer address {}'.format(signer_address))
signer = EIP155Signer(keystore)

conn = EthHTTPConnection(args.p)

nonce_oracle = None
if args.nonce != None:
    nonce_oracle = OverrideNonceOracle(signer_address, args.nonce)
else:
    nonce_oracle = RPCNonceOracle(signer_address, conn)

gas_oracle = None
if args.price or args.gas != None:
    gas_oracle = OverrideGasOracle(price=args.price, limit=args.gas, conn=conn)
else:
    gas_oracle = RPCGasOracle(conn)


chain_spec = ChainSpec.from_chain_str(args.i)

value = args.amount

send = args.s

g = Gas(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)


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
    if logg.isEnabledFor(logging.DEBUG):
        logg.debug('sender {} balance before: {}'.format(signer_address, balance(signer_address)))
        logg.debug('recipient {} balance before: {}'.format(recipient, balance(recipient)))
     
    (tx_hash_hex, o) = g.create(signer_address, recipient, value)

    if send:
        conn.do(o)
        if block_last:
            r = conn.wait(tx_hash_hex)
            if logg.isEnabledFor(logging.DEBUG):
                logg.debug('sender {} balance after: {}'.format(signer_address, balance(signer_address)))
                logg.debug('recipient {} balance after: {}'.format(recipient, balance(recipient)))
            if r['status'] == 0:
                logg.critical('VM revert. Wish I could tell you more')
                sys.exit(1)
        print(tx_hash_hex)
    else:
        if logg.isEnabledFor(logging.INFO):
            io_str = io.StringIO()
            decode_for_puny_humans(o['params'][0], chain_spec, io_str)
            print(io_str.getvalue())
        else:
            print(o['params'][0])
 


if __name__ == '__main__':
    main()
