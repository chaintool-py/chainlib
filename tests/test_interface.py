# standard imports
import unittest
from unittest.mock import Mock
import logging

# local imports
from chainlib.interface import ChainInterface

logg = logging.getLogger()


# replace with mocker
def block_from_src(src):
    logg.debug('from src called with ' + src)


class TestInterface(unittest.TestCase):

    def test_interface_set(self):
        ifc = ChainInterface()
        block_from_src = Mock()
        ifc.set('block_from_src', block_from_src)
        ifc.block_from_src('foo')
        block_from_src.assert_called()


if __name__ == '__main__':
    unittest.main()
