# standard imports
import enum

# local imports
from .tx import Tx
from .src import Src


class BlockSpec(enum.IntEnum):
    """General-purpose block-height value designators
    """
    PENDING = -1
    LATEST = 0


class Block(Src):
    """Base class to extend for implementation specific block object.
    """
 
    tx_generator = Tx

    def __init__(self, src=None, dialect_filter=None):
        self.number = None
        self.txs = []
        self.author = None

        self.get_tx = self.tx_index_by_hash
        self.tx = self.tx_by_index

        self.fee_limit = 0
        self.fee_cost = 0
        self.parent_hash = None

        self.extra = {}

        super(Block, self).__init__(src=src, dialect_filter=dialect_filter)

        self.load_src(dialect_filter=dialect_filter)


    def tx_by_index(self, idx):
        """Return transaction object for transaction data at given index.

        :param idx: Transaction index
        :type idx: int
        :rtype: chainlib.tx.Tx
        :returns: Transaction object
        """
        return self.tx_generator(self.txs[idx], self)


    def tx_index_by_hash(self, hsh):
        for tx in self.tx:
            if tx == hsh:
                return tx
        return -1


    def __str__(self):
        return 'block {} {} ({} txs)'.format(self.number, self.hash, len(self.txs))
