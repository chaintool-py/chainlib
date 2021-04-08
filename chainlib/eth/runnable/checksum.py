# standard imports
import sys

# local imports
from chainlib.eth.address import to_checksum_address


print(to_checksum_address(sys.argv[1]))
