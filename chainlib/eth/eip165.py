# standard imports
from chainlib.eth.constant import ZERO_ADDRESS

# external imports
from chainlib.jsonrpc import (
        jsonrpc_template,
        )
from hexathon import (
        add_0x,
        )
from chainlib.eth.contract import (
        ABIContractEncoder,
        ABIContractDecoder,
        ABIContractType,
        abi_decode_single,
        )
from chainlib.eth.tx import TxFactory


class EIP165(TxFactory):

    def supports_interface(self, contract_address, interface_sum, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('supportsInterface')
        enc.typ(ABIContractType.BYTES4)
        enc.bytes4(interface_sum)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        return o


    @classmethod
    def parse_supports_interface(self, v):
        return abi_decode_single(ABIContractType.BOOLEAN, v)
