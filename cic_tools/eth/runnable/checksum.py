# standard imports
import sys

# local imports
from cic_tools.eth.checksum import to_checksum


print(to_checksum(sys.argv[1]))
