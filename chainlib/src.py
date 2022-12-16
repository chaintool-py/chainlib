# standard imports
import enum


class SrcItem(enum.Enum):
    AUTO = 0
    SRC = 1
    HASH = 2
    ADDRESS = 3
    PAYLOAD = 4


class Src:

    def __init__(self, src=None, dialect_filter=None):
        self.__src = None
        self.__hash = None
        self.__wire = None
        if src != None:
            self.apply_src(src, dialect_filter=dialect_filter)


    @classmethod
    def src_normalize(self, v):
        return v


    def src_validate(self, v):
        return v


    def apply_src(self, src, dialect_filter=None):
        src = self.src_normalize(src)
        if dialect_filter != None:
            src = dialect_filter.apply_src(src)
        self.__src = self.src_validate(src)
        return self.__src


    @property
    def src(self):
        return self.__src


    def set_hash(self, hsh):
        self.__hash = hsh


    @property
    def hash(self):
        return self.__hash


    def set_wire(self, v):
        self.__wire = v

    
    @property
    def wire(self):
        return self.__wire


    def normal(self, v, typ=SrcItem.AUTO):
        if typ == SrcItem.SRC:
            return self.src_normalize(v)
        return v


    def safe(self, v, typ=SrcItem.AUTO):
        return v


    def display(self, v, typ=SrcItem.AUTO):
        return v


    @classmethod
    def from_src(cls, src):
        """Instantiate an implementation specific block object from the given block representation.

        :param src: Block representation
        :type src: dict
        :rtype: chainlib.block.Block
        :returns: Block object
        """
        return cls(src)


    def __repr__(self):
        return self.__src


    def load_src(self, dialect_filter=None):
        raise NotImplementedError()


