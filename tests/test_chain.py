# standard imports
import unittest
import logging

# local imports
from chainlib.chain import ChainSpec

# test imports
from tests.base import TestBase

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()
logg.setLevel(logging.DEBUG)


class TestChain(TestBase):

    def test_chain_spec_str(self):
        s = ChainSpec('foo', 'bar', 3)
        self.assertEqual('foo:bar:3', str(s))

        s = ChainSpec('foo', 'bar', 3, 'baz')
        self.assertEqual('foo:bar:3:baz', str(s))


        s = ChainSpec('foo', 'bar', 3, 'baz', ['inky', 'pinky', 'blinky'])
        self.assertEqual('foo:bar:3:baz:inky:pinky:blinky', str(s))


    def test_chain_spec(self):
        s = ChainSpec.from_chain_str('foo:bar:3')
        s = ChainSpec.from_chain_str('foo:bar:3:baz')
        s = ChainSpec.from_chain_str('foo:bar:3:baz:inky:pinky:blinky')

        with self.assertRaises(ValueError):
            s = ChainSpec.from_chain_str('foo:bar:a')
            s = ChainSpec.from_chain_str('foo:bar')
            s = ChainSpec.from_chain_str('foo')
            s = ChainSpec.from_chain_str('foo1:bar:3')
            s = ChainSpec.from_chain_str('foo:bar2:3')


    def test_chain_spec_dict(self):
        ss = 'foo:bar:3:baz:inky:pinky:blinky'
        c = ChainSpec.from_chain_str(ss)
        d = c.asdict()
        self.assertEqual(d['arch'], 'foo')
        self.assertEqual(d['fork'], 'bar')
        self.assertEqual(d['network_id'], 3)
        self.assertEqual(d['common_name'], 'baz')
        self.assertEqual(d['custom'], ['inky', 'pinky', 'blinky'])
        cc = ChainSpec.from_dict(d)
        self.assertEqual(ss, str(cc))

        d = c.asdict(use_custom=False)
        cc = ChainSpec.from_dict(d)
        self.assertEqual(str(cc), 'foo:bar:3:baz')

        d = c.asdict(use_common_name=False)
        cc = ChainSpec.from_dict(d)
        self.assertEqual(str(cc), 'foo:bar:3')

    def test_chain_spec_compare(self):
        a = 'foo:bar:42:baz'
        b = 'foo:bar:42:barbar'
        c = 'foo:bar:42:baz:inky:pinky:blinky'

        ca = ChainSpec.from_chain_str(a)
        cb = ChainSpec.from_chain_str(b)

        self.assertTrue(ca.is_same_as(cb))
        self.assertFalse(ca.is_same_as(cb, use_common_name=True))

        cc = ChainSpec.from_chain_str(c)
        logg.debug('chain_spec_cmp ' + str(cc.o))
        self.assertTrue(ca.is_same_as(cc))
        self.assertTrue(ca.is_same_as(cc, use_common_name=True))
        self.assertFalse(ca.is_same_as(cc, use_common_name=True, use_custom=True))



if __name__ == '__main__':
    unittest.main()
