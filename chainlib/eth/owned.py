# external imports
from hexathon import (
        add_0x,
    )

# local imports
from chainlib.eth.contract import (
        ABIContractEncoder,
        ABIContractDecoder,
        ABIContractType,
        abi_decode_single,
    )
from chainlib.jsonrpc import jsonrpc_template
from chainlib.eth.tx import (
        TxFactory,
        TxFormat,
        )
from chainlib.eth.constant import ZERO_ADDRESS

class EIP173(TxFactory):

    def transfer_ownership(self, contract_address, sender_address, new_owner_address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('transferOwnership')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(new_owner_address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def owner(self, contract_address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('owner')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        return o


    @classmethod
    def parse_owner(self, v):
        return abi_decode_single(ABIContractType.ADDRESS, v)


class Owned(EIP173):

    def accept_ownership(self, contract_address, sender_address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('acceptOwnership')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def take_ownership(self, contract_address, sender_address, resource_address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('takeOwnership')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(resource_address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx
