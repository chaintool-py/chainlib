import unittest

from chainlib.chain import ChainSpec

from tests.base import TestBase


class TestChain(TestBase):

    def test_chain_spec(self):

        s = ChainSpec.from_chain_str('foo:bar:3')
        s = ChainSpec.from_chain_str('foo:bar:3:baz')

        with self.assertRaises(ValueError):
            s = ChainSpec.from_chain_str('foo:bar:a')
            s = ChainSpec.from_chain_str('foo:bar')
            s = ChainSpec.from_chain_str('foo')


if __name__ == '__main__':
    unittest.main()
