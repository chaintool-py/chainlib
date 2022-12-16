# standard imports
import unittest

# local imports
from chainlib.src import Src
from chainlib.tx import (
        Tx,
        TxResult,
        )
from chainlib.block import Block
from chainlib.status import Status

class TestBlock(Block):

    def load_src(self, dialect_filter=None):
        self.number = self.src['number']


class TestTx(Tx):

    def load_src(self, dialect_filter=None):
        self.foo = self.src['foo']


class TestTxResult(TxResult):

    def load_src(self, dialect_filter=None):
        self.bar = self.src['bar']


class TestSrc(unittest.TestCase):

    def test_basic(self):
        v = {'foo': 'bar'}
        src = Src(v)
        self.assertEqual(src.src, v)


    def test_block_basic(self):
        v = {'number': 42}
        block = TestBlock(v)
        self.assertEqual(block.src, v)
        self.assertEqual(block.number, 42)


    def test_tx_basic(self):
        v = {'foo': 'bar'}
        tx = TestTx(v)
        self.assertEqual(tx.src, v)
        self.assertEqual(tx.foo, 'bar')

        v = {'bar': 'baz'}
        result = TestTxResult(v)
        self.assertEqual(result.src, v)
        self.assertEqual(result.status, Status.UNKNOWN)
        self.assertEqual(result.bar, 'baz')


    def test_apply(self):
        vt = {'foo': 'bar'}
        tx = TestTx(vt)

        vb = {'number': 42}
        block = TestBlock(vb)

        vr = {'bar': 'baz'}
        result = TestTxResult(vr)

        tx.apply_block(block)

        tx.apply_result(result)

        self.assertEqual(tx.src, vt)
        self.assertEqual(tx.status, Status.UNKNOWN)
        self.assertEqual(tx.status_name, Status.UNKNOWN.name)
        self.assertEqual(tx.foo, 'bar')
        self.assertEqual(tx.result.bar, 'baz')

        tx = TestTx(vt, block=block, result=result)

        self.assertEqual(tx.src, vt)
        self.assertEqual(tx.status, Status.UNKNOWN)
        self.assertEqual(tx.status_name, Status.UNKNOWN.name)
        self.assertEqual(tx.foo, 'bar')
        self.assertEqual(tx.result.bar, 'baz')


    def test_from(self):
        v = {'foo': 'bar'}
        tx = TestTx.from_src(v)
        self.assertEqual(tx.src, v)
        self.assertEqual(tx.foo, 'bar')


if __name__ == '__main__':
    unittest.main()
