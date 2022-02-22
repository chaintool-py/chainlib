import os
import sys
import argparse
import tempfile
import shutil

from hexathon import strip_0x, add_0x

from chainlib.cli.man import DocGenerator
from chainlib.cli.base import argflag_std_base

argparser = argparse.ArgumentParser()
argparser.add_argument('-b', default=add_0x(hex(argflag_std_base)), help='argument flag bitmask')
argparser.add_argument('-n', help='tool name to use for man filename')
argparser.add_argument('-d', default='.', help='output directory')
argparser.add_argument('header_file', help='groff file containing heading, synopsis and description')
args = argparser.parse_args(sys.argv[1:])

#b = bytes.fromhex(strip_0x(sys.argv[1]))
b = bytes.fromhex(strip_0x(args.b))
g = DocGenerator(int.from_bytes(b, byteorder='little'))
g.process()

f = open(args.header_file)
head = f.read()
f.close()

toolname = args.n
if toolname == None:
    parts = os.path.splitext(os.path.basename(args.header_file))
    toolname = parts[0]

(fd, fp) = tempfile.mkstemp()
f = os.fdopen(fd, 'w')
f.write(head)
f.write(str(g))
f.close()

dest = os.path.join(args.d, toolname + '.1')
shutil.copyfile(fp, dest)

os.unlink(fp)
