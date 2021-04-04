# local imports
from chainlib.jsonrpc import jsonrpc_template 


def new_account(passphrase=''):
    o = jsonrpc_template()
    o['method'] = 'personal_newAccount'
    o['params'] = [passphrase]
    return o


def sign_transaction(payload):
    o = jsonrpc_template()
    o['method'] = 'eth_signTransaction'
    o['params'] = [payload]
    return o


def sign_message(address, payload):
    o = jsonrpc_template()
    o['method'] = 'eth_sign'
    o['params'] = [address, payload]
    return o
