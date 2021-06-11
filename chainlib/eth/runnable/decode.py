#!python3

"""Decode raw transaction

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
import select

# external imports
from chainlib.eth.tx import unpack
from chainlib.chain import ChainSpec

# local imports
from chainlib.eth.runnable.util import decode_for_puny_humans


logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

default_abi_dir = os.environ.get('ETH_ABI_DIR', '/usr/share/local/cic/solidity/abi')
default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

def stdin_arg():
    h = select.select([sys.stdin], [], [], 0)
    if len(h[0]) > 0:
        v = h[0][0].read()
        return v.rstrip()
    return None

argparser = argparse.ArgumentParser()
argparser.add_argument('-i', '--chain-id', dest='i', default='evm:ethereum:1', type=str, help='Numeric network id')
argparser.add_argument('tx', type=str, nargs='?', default=stdin_arg(), help='hex-encoded signed raw transaction')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
args = argparser.parse_args()

if args.tx == None:
    argparser.error('need first positional argument or value from stdin')

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

chain_spec = ChainSpec.from_chain_str(args.i)


def main():
    tx_raw = args.tx
    decode_for_puny_humans(tx_raw, chain_spec, sys.stdout)

if __name__ == '__main__':
    main()
