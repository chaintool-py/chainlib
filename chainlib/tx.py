# local imports
from .status import Status
from .src import Src


class Tx(Src):
    """Base class to extend for implementation specific transaction objects.

    :param src: Transaction representation source
    :type src: dict
    :param block: Block in which transaction has been included
    :type block: chainlib.block.Block
    """

    def __init__(self, src=None, block=None, result=None, strict=False, dialect_filter=None):
        self.block = block
        self.index = -1

        self.fee_limit = None
        self.fee_price = None

        self.nonce = None
        self.value = 0

        self.outputs = []
        self.inputs = []
        self.payload = None

        self.result = None
    
        super(Tx, self).__init__(src, dialect_filter=dialect_filter)

        self.load_src(dialect_filter=dialect_filter)

        if block != None:
            self.apply_block(block, dialect_filter=dialect_filter)

        if result != None:
            self.apply_result(result, dialect_filter=dialect_filter)


    def apply_result(self, result, dialect_filter=None):
        self.result = result


    def apply_block(self, block, dialect_filter=None):
        self.block = block


    @property
    def status(self):
        if self.result == None:
            return None
        return self.result.status

    
    @property
    def status_name(self):
        if self.result == None:
            return None
        return self.result.status.name


    def generate_wire(self, chain_spec):
        pass
   

    def as_dict(self):
        raise NotImplementedError()


    def __str__(self):
        if self.block != None:
            return 'tx {} status {} block {} index {}'.format(self.display_hash(), self.status_name(), self.block.number, self.index)
        else:
            return 'tx {} status {}'.format(self.display_hash(), self.hash, self.status_name())


class TxResult(Src):

    def __init__(self, src=None, dialect_filter=None):
        self.status = Status.UNKNOWN
        self.tx_index = None
        self.block_hash = None
        self.fee_cost = 0
        super(TxResult, self).__init__(src=src)

        self.load_src(dialect_filter=dialect_filter)
