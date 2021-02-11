# standard imports
import sys

# local imports
from chainlib.eth.address import to_checksum


print(to_checksum(sys.argv[1]))
