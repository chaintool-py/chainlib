#!python3

"""Token balance query script

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import os
import json
import argparse
import logging
import enum

# third-party imports
from hexathon import (
        add_0x,
        strip_0x,
        even,
        )
import sha3
from eth_abi import encode_single

# local imports
from chainlib.eth.address import to_checksum
from chainlib.eth.rpc import (
        jsonrpc_template,
        jsonrpc_result,
        )
from chainlib.eth.connection import HTTPConnection
from chainlib.eth.tx import Tx
from chainlib.eth.block import Block

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

default_abi_dir = os.environ.get('ETH_ABI_DIR', '/usr/share/local/cic/solidity/abi')
default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default=default_eth_provider, type=str, help='Web3 provider url (http only)')
argparser.add_argument('-t', '--token-address', dest='t', type=str, help='Token address. If not set, will return gas balance')
argparser.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Auto-convert address to checksum adddress')
argparser.add_argument('--abi-dir', dest='abi_dir', type=str, default=default_abi_dir, help='Directory containing bytecode and abi (default {})'.format(default_abi_dir))
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('tx_hash', type=str, help='Transaction hash')
args = argparser.parse_args()


if args.v:
    logg.setLevel(logging.DEBUG)

conn = HTTPConnection(args.p)

tx_hash = args.tx_hash


class Status(enum.Enum):
    UNCONFIRMED = -1
    REVERTED = 0
    SUCCESS = 1


def main():
    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionByHash'
    o['params'].append(tx_hash)
    tx_src = conn.do(o)

    tx = None
    status = -1
    if tx_src['blockHash'] != None:
        o = jsonrpc_template()
        o['method'] = 'eth_getBlockByHash'
        o['params'].append(tx_src['blockHash'])
        o['params'].append(True)
        block_src = conn.do(o)
        block = Block(block_src)
        for t in block.txs:
            if t['hash'] == tx_hash:
                tx = Tx(t, block)
                break
        o = jsonrpc_template()
        o['method'] = 'eth_getTransactionReceipt'
        o['params'].append(tx_hash)
        rcpt = conn.do(o)
        status = int(strip_0x(rcpt['status']), 16)

    if tx == None:
        tx = Tx(tx_src)
    print(tx)
    status_name = Status(status).name
    print('status {}'.format(status_name))


if __name__ == '__main__':
    main()
