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
import enum

# external imports
from hexathon import (
        add_0x,
        strip_0x,
        )
import sha3

# local imports
from chainlib.eth.address import to_checksum
from chainlib.jsonrpc import (
        jsonrpc_template,
        jsonrpc_result,
        )
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.tx import Tx
from chainlib.eth.address import to_checksum_address
from chainlib.eth.block import Block
from chainlib.chain import ChainSpec
from chainlib.status import Status

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

default_abi_dir = os.environ.get('ETH_ABI_DIR', '/usr/share/local/cic/solidity/abi')
default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default=default_eth_provider, type=str, help='Web3 provider url (http only)')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-t', '--token-address', dest='t', type=str, help='Token address. If not set, will return gas balance')
argparser.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Auto-convert address to checksum adddress')
argparser.add_argument('--abi-dir', dest='abi_dir', type=str, default=default_abi_dir, help='Directory containing bytecode and abi (default {})'.format(default_abi_dir))
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('item', type=str, help='Item to get information for (address og transaction)')
args = argparser.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

conn = EthHTTPConnection(args.p)

#tx_hash = add_0x(args.tx_hash)
item = add_0x(args.item)


def get_transaction(conn, tx_hash):
    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionByHash'
    o['params'].append(tx_hash)
    tx_src = conn.do(o)
    if tx_src == None:
        logg.error('Transaction {} not found'.format(tx_hash))
        sys.exit(1)

    tx = None
    status = -1
    rcpt = None

    o = jsonrpc_template()
    o['method'] = 'eth_getTransactionReceipt'
    o['params'].append(tx_hash)
    rcpt = conn.do(o)
    #status = int(strip_0x(rcpt['status']), 16)

    if tx == None:
        tx = Tx(tx_src)
    if rcpt != None:
        tx.apply_receipt(rcpt)
    return tx


def get_address(conn, address):
    o = jsonrpc_template()
    o['method'] = 'eth_getCode'
    o['params'].append(address)
    o['params'].append('latest')
    code = conn.do(o)
    
    content = strip_0x(code, allow_empty=True)
    if len(content) == 0:
        return None

    return content


def main():
    r = None
    if len(item) > 42:
        r = get_transaction(conn, item)
    elif args.u or to_checksum_address(item):
        r = get_address(conn, item)
    print(r)


if __name__ == '__main__':
    main()
