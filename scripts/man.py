import sys
from hexathon import strip_0x
from chainlib.cli.man import DocGenerator

b = bytes.fromhex(strip_0x(sys.argv[1]))
g = DocGenerator(int.from_bytes(b, byteorder='little'))
g.process()
print(g)
