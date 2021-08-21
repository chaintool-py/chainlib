# standard imports
import enum

class Status(enum.Enum):
    """Representation of transaction status in network.
    """
    PENDING = 0
    SUCCESS = 1
    ERROR = 2
