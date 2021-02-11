# third-party imports
import sha3
from hexathon import add_0x
from eth_abi import encode_single
from crypto_dev_signer.eth.transaction import EIP155Transaction

# local imports
from .hash import (
        keccak256_hex_to_hex,
        keccak256_string_to_hex,
        )
from .constant import ZERO_ADDRESS
from .rpc import jsonrpc_template
from .tx import TxFactory
        

# TODO: move to cic-contracts
erc20_balance_signature = keccak256_string_to_hex('balanceOf(address)')[:8]
erc20_decimals_signature = keccak256_string_to_hex('decimals()')[:8]
erc20_transfer_signature = keccak256_string_to_hex('transfer(address,uint256)')[:8]


class ERC20TxFactory(TxFactory):

    def build(self, tx):
        txe = EIP155Transaction(tx, tx['nonce'], tx['chainId'])
        self.signer.signTransaction(txe)
        tx_raw = txe.rlp_serialize()
        tx_raw_hex = add_0x(tx_raw.hex())
        tx_hash_hex = add_0x(keccak256_hex_to_hex(tx_raw_hex))

        o = jsonrpc_template()
        o['method'] = 'eth_sendRawTransaction'
        o['params'].append(tx_raw_hex)

        return (tx_hash_hex, o)


    def erc20_balance(self, contract_address, address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        data = erc20_balance_signature
        data += encode_single('address', address).hex()
        data = add_0x(data)
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        return o


    def erc20_decimals(self, contract_address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        data = add_0x(erc20_decimals_signature)
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        return o


    def erc20_transfer(self, contract_address, sender_address, recipient_address, value):
        data = erc20_transfer_signature
        data += encode_single('address', recipient_address).hex()
        data += encode_single('uint256', value).hex()
        data = add_0x(data)
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        return self.build(tx)
