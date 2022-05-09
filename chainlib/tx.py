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

    def __init__(self, src=None, block=None, result=None, strict=False):
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
    
        self.generate_wire = self.wire

        super(Tx, self).__init__(src)

        if block != None:
            self.apply_block(block)

        if result != None:
            self.apply_result(result)


    def apply_result(self, result):
        self.result = result


    def apply_block(self, block):
        self.block = block


    def status(self):
        if self.result == None:
            return None
        return self.result.status


    def status_name(self):
        if self.result == None:
            return None
        return self.result.status.name


    def wire(self):
        raise NotImplementedError()


    def as_dict(self):
        raise NotImplementedError()


    def __str__(self):
        if self.block != None:
            return 'tx {} status {} block {} index {}'.format(self.display_hash(), self.status_name(), self.block.number, self.index)
        else:
            return 'tx {} status {}'.format(self.display_hash(), self.hash, self.status_name())


class TxResult(Src):

    def __init__(self, src):
        self.status = Status.UNKNOWN
        super(TxResult, self).__init__(src)
