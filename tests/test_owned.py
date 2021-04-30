# standard imports
import unittest
import os
import logging

# local imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.gas import OverrideGasOracle
from chainlib.connection import RPCConnection
from chainlib.eth.tx import (
        TxFactory,
        receipt,
        )
from chainlib.eth.eip165 import EIP165

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

script_dir = os.path.realpath(os.path.dirname(__file__))


class TestOwned(EthTesterCase):

    def setUp(self):
        super(TestOwned, self).setUp()
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)

        f = open(os.path.join(script_dir, 'testdata', 'Owned.bin'))
        code = f.read()
        f.close()

        txf = TxFactory(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        tx = txf.template(self.accounts[0], None, use_nonce=True)
        tx = txf.set_code(tx, code)
        (tx_hash_hex, o) = txf.build(tx)

        r = self.conn.do(o)
        logg.debug('deployed with hash {}'.format(r))

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.address = r['contract_address']

    
    def test_owned(self):
        pass


if __name__ == '__main__':
    unittest.main()
