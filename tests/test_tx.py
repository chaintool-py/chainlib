# standard imports
import unittest 

# local imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.gas import (
        RPCGasOracle,
        Gas,
        )
from chainlib.eth.tx import (
        unpack,
        TxFormat,
        )
from hexathon import strip_0x

class TxTestCase(EthTesterCase):

    def test_tx_reciprocal(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        gas_oracle = RPCGasOracle(self.rpc)
        c = Gas(signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, chain_spec=self.chain_spec)
        (tx_hash_hex, o) = c.create(self.accounts[0], self.accounts[1], 1024, tx_format=TxFormat.RLP_SIGNED)
        tx = unpack(bytes.fromhex(strip_0x(o)), self.chain_spec)
        self.assertEqual(tx['from'], self.accounts[0])
        self.assertEqual(tx['to'], self.accounts[1])


if __name__ == '__main__':
    unittest.main()
