# standard imports
import enum

# local imports
from chainlib.tx import Tx


class BlockSpec(enum.IntEnum):
    """General-purpose block-height value designators
    """
    PENDING = -1
    LATEST = 0


class Block:
    """Base class to extend for implementation specific block object.
    """
 
    tx_generator = Tx


    def src(self):
        """Return implementation specific block representation.

        :rtype: dict
        :returns: Block representation
        """
        return self.block_src


    def tx(self, idx):
        """Return transaction object for transaction data at given index.

        :param idx: Transaction index
        :type idx: int
        :rtype: chainlib.tx.Tx
        :returns: Transaction object
        """
        return self.tx_generator(self.txs[idx], self)


    def tx_src(self, idx):
        """Return implementation specific transaction representation for transaction data at given index

        :param idx: Transaction index
        :type idx: int
        :rtype: chainlib.tx.Tx
        :returns: Transaction representation
        """
        return self.txs[idx]


    def __str__(self):
        return 'block {} {} ({} txs)'.format(self.number, self.hash, len(self.txs))


    @classmethod
    def from_src(cls, src):
        """Instantiate an implementation specific block object from the given block representation.

        :param src: Block representation
        :type src: dict
        :rtype: chainlib.block.Block
        :returns: Block object
        """
        return cls(src)
