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
from chainlib.eth.owned import (
        EIP173,
        Owned,
        )

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
        c = EIP173(self.chain_spec)
        o = c.owner(self.address, sender_address=self.accounts[0])
        r = self.conn.do(o)
        owner = c.parse_owner(r)
        self.assertEqual(owner, self.accounts[0])


    def test_transfer_ownership(self):
        nonce_oracle = RPCNonceOracle(self.accounts[2], self.conn)
        gas_oracle = OverrideGasOracle(limit=8000000, conn=self.conn)
        c = EIP173(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[2], self.accounts[1])
        r = self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 0)
        
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EIP173(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[0], self.accounts[1])
        r = self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)
       

    def test_accept_ownership(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        gas_oracle = OverrideGasOracle(limit=8000000, conn=self.conn)
        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[0], self.accounts[1])
        r = self.conn.do(o)

        nonce_oracle = RPCNonceOracle(self.accounts[2], self.conn)
        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
        (tx_hash_hex, o) = c.accept_ownership(self.address, self.accounts[2])
        r = self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 0)

        nonce_oracle = RPCNonceOracle(self.accounts[1], self.conn)
        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
        (tx_hash_hex, o) = c.accept_ownership(self.address, self.accounts[1])
        r = self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.owner(self.address, sender_address=self.accounts[0])
        r = self.conn.do(o)
        owner = c.parse_owner(r)
        self.assertEqual(owner, self.accounts[1])


    def test_take_ownership(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        gas_oracle = OverrideGasOracle(limit=8000000, conn=self.conn)
        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[0], self.address)
        r = self.conn.do(o)

        (tx_hash_hex, o) = c.take_ownership(self.address, self.accounts[0], self.address)
        r = self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.owner(self.address, sender_address=self.accounts[0])
        r = self.conn.do(o)
        owner = c.parse_owner(r)
        self.assertEqual(owner, self.address)


if __name__ == '__main__':
    unittest.main()
