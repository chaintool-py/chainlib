import sha3
import uuid

from hexathon import add_0x
from eth_abi import encode_single

from .hash import keccak256_string_to_hex
from .constant import ZERO_ADDRESS


# TODO: move to cic-contracts
erc20_balance_signature = keccak256_string_to_hex('balanceOf(address)')[:8]
erc20_decimals_signature = keccak256_string_to_hex('decimals()')[:8]


def jsonrpc_template():
    return {
        'jsonrpc': '2.0',
        'id': str(uuid.uuid4()),
        'method': None,
        'params': [],
            }


def erc20_balance(contract_address, address, sender_address=ZERO_ADDRESS):
    o = jsonrpc_template()
    o['method'] = 'eth_call'
    data = erc20_balance_signature
    data += encode_single('address', address).hex()
    data = add_0x(data)
    a = call(contract_address, data=data)
    o['params'].append(a)
    o['params'].append('latest')
    return o


def erc20_decimals(contract_address, sender_address=ZERO_ADDRESS):
    o = jsonrpc_template()
    o['method'] = 'eth_call'
    arg = add_0x(erc20_decimals_signature)
    #o['params'].append(arg)
    a = call(contract_address, arg)
    o['params'].append(a)
    o['params'].append('latest')
    return o


def call(contract_address, data, sender_address=ZERO_ADDRESS):
    return {
        'from': sender_address,
        'to': contract_address,
        'data': data,
            }


def jsonrpc_result(o, ep):
    if o.get('error') != None:
        raise ep.translate(o)
    return o['result']


