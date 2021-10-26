import unittest

from chainlib.chain import ChainSpec

from tests.base import TestBase


class TestChain(TestBase):

    def test_chain_spec_str(self):
        s = ChainSpec('foo', 'bar', 3, 'baz')
        self.assertEqual('foo:bar:3:baz', str(s))

        s = ChainSpec('foo', 'bar', 3)
        self.assertEqual('foo:bar:3', str(s))

    def test_chain_spec(self):

        s = ChainSpec.from_chain_str('foo:bar:3')
        s = ChainSpec.from_chain_str('foo:bar:3:baz')

        with self.assertRaises(ValueError):
            s = ChainSpec.from_chain_str('foo:bar:a')
            s = ChainSpec.from_chain_str('foo:bar')
            s = ChainSpec.from_chain_str('foo')


    def test_chain_spec_dict(self):
        s = 'foo:bar:3:baz'
        c = ChainSpec.from_chain_str('foo:bar:3:baz')
        d = c.asdict()
        self.assertEqual(d['arch'], 'foo')
        self.assertEqual(d['fork'], 'bar')
        self.assertEqual(d['network_id'], 3)
        self.assertEqual(d['common_name'], 'baz')
        cc = ChainSpec.from_dict(d)
        self.assertEqual(s, str(cc))



if __name__ == '__main__':
    unittest.main()
