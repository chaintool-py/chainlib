# standard imports
import sys

# external imports
from hexathon import strip_0x

# local imports
from chainlib.eth.address import to_checksum_address

def main():
    print(to_checksum_address(strip_0x(sys.argv[1])))


if __name__ == '__main__':
    main()
