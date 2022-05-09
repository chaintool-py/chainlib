# standard imports
import enum

class Status(enum.Enum):
    """Representation of transaction status in network.
    """
    UNKNOWN = -1
    PENDING = 0
    SUCCESS = 1
    ERROR = 2
