# standard imports
import argparse
import sys
import math

# local imports
from chainlib.cli.arg import ArgFlag


def value_int(v):
    return str(v)

def value_hex(v):
    sz = math.log(v, 2)
    if v == 0:
        return "00"
    sz = math.floor(sz)
    sz = (sz / 8) + 1
    return '0x' + v.to_bytes(int(sz), byteorder='big').hex()

argflag = ArgFlag()

argparser = argparse.ArgumentParser()
argparser.add_argument('-l', '--list', action='store_true', help='List all flag names and values')
argparser.add_argument('-x', '--hex', action='store_true', help='Output all values in hex')
argparser.add_argument('-0', dest='nonl', action='store_true', help='Omit newline in single flag output')
argparser.add_argument('flag', type=str, nargs='*', help='One or more flag name to calculate flag value for')
args = argparser.parse_args(sys.argv[1:])

m = value_int
if args.hex:
    m = value_hex

if args.list:
    o = dict(argflag)
    for k in o.keys():
        r = k.split("=")
        v = m(o[k])
        if len(r) == 1:
            print(k + ' ' + v)
        else:
            print(r[0] + ' ' + v + ' (' + r[1] + ')')
    sys.exit(0)

if len(args.flag) == 0:
    sys.stdout.write(m(argflag.all))
else:
    r = 0
    for k in args.flag:
        r += argflag.val(k)
    sys.stdout.write(m(r))

if not args.nonl:
    sys.stdout.write("\n")
