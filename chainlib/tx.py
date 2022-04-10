class Tx:
    """Base class to extend for implementation specific transaction objects.

    :param src: Transaction representation source
    :type src: dict
    :param block: Block in which transaction has been included
    :type block: chainlib.block.Block
    """

    def __init__(self, src, block=None):
        self.src = src
        self.block = block
        self.block_src = None
        self.index = None
