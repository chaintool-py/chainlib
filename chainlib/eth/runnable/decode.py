#!python3

"""Decode raw transaction

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import os
import json
import argparse
import logging

# third-party imports
from chainlib.eth.tx import unpack_signed


logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

default_abi_dir = os.environ.get('ETH_ABI_DIR', '/usr/share/local/cic/solidity/abi')
default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-i', '--chain-id', dest='i', type=str, help='Numeric network id')
argparser.add_argument('tx', type=str, help='hex-encoded signed raw transaction')
args = argparser.parse_args()

if args.v:
    logg.setLevel(logging.DEBUG)

(chain_name, chain_id) = args.i.split(':')


def main():
    tx_raw = args.tx
    if tx_raw[:2] == '0x':
        tx_raw = tx_raw[2:]
    tx_raw_bytes = bytes.fromhex(tx_raw)
    tx = unpack_signed(tx_raw_bytes, int(chain_id))
    for k in tx.keys():
        print('{}: {}'.format(k, tx[k]))


if __name__ == '__main__':
    main()
