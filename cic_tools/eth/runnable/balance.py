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

# third-party imports
from hexathon import (
        add_0x,
        strip_0x,
        even,
        )
import sha3
from eth_abi import encode_single

# local imports
from cic_tools.eth.address import to_checksum
from cic_tools.eth.method import (
        jsonrpc_template,
        erc20_balance,
        erc20_decimals,
        jsonrpc_result,
        )
from cic_tools.eth.connection import HTTPConnection


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
argparser.add_argument('account', type=str, help='Account address')
args = argparser.parse_args()


if args.v:
    logg.setLevel(logging.DEBUG)

conn = HTTPConnection(args.p)

def main():
    account = to_checksum(args.account)
    if not args.u and account != add_0x(args.account):
        raise ValueError('invalid checksum address')
    
    r = None
    decimals = 18
    if args.t != None:
        # determine decimals
        decimals_o = erc20_decimals(args.t)
        r = conn.do(decimals_o)
        decimals = int(strip_0x(r), 16)

        # get balance
        balance_o = erc20_balance(args.t, account)
        r = conn.do(balance_o)

    else:
        o = jsonrpc_template()
        o['method'] = 'eth_getBalance'
        o['params'].append(account)
        r = conn.do(o)
   
    hx = strip_0x(r)
    balance = int(hx, 16)
    logg.debug('balance {} = {} decimals {}'.format(even(hx), balance, decimals))

    balance_str = str(balance)
    balance_len = len(balance_str)
    if balance_len < 19:
        print('0.{}'.format(balance_str.zfill(decimals)))
    else:
        offset = balance_len-decimals
        print('{}.{}'.format(balance_str[:offset],balance_str[offset:]))


if __name__ == '__main__':
    main()
