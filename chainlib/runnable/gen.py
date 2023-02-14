# standard imports
import argparse
import sys
import os
import logging

# local imports
from chainlib.cli.gen import find_chainlib_modules

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()


ap = argparse.ArgumentParser()
ap.add_argument('-v', action='store_true', help='verbose logging')
ap.add_argument('-vv', action='store_true', help='very verbose logging')
ap.add_argument('-k', action='store_true', help='return keys for command')
ap.add_argument('module', type=str, help='module to locate and execute')
ap.add_argument('command', type=str, nargs='?', help='command to execute on module. default command will be executed if not specified')
ap.add_argument('arg', type=str, nargs=argparse.REMAINDER)
args = ap.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

def parse_remaining(rargs):
    rargsr = []
    for v in rargs:
        if v == '-vv':
            logg.setLevel(logging.DEBUG)
        elif v == '-v':
            logg.setLevel(logging.INFO)
        elif v == '-k':
            return None
        else:
            rargsr.append(v)
    r = {}
    logg.debug('parsing rargs {}'.format(rargsr))
    while True:
        try:
            pfx = rargsr.pop(0)
        except IndexError:
            break
        if len(pfx) < 3 or pfx[:2] != '--':
            raise ValueError('unexpected arg element: {}'.format(pfx))
        k = pfx[2:]
        try:
            v = rargsr.pop(0)
        except IndexError:
            raise ValueError('missing value for attribute: {}'.format(pfx))
        r[k] = v
    return r


def default_handler(m, cmd, args, is_key_query=False):
    r = None

    if is_key_query:
        r = m.args(cmd)
        print('required: ' + ', '.join(r[0]))
        print('optional: ' + ', '.join(r[1]))
        return

    fn = getattr(m, cmd)
    if args == None:
        r = fn()
    else:
        r = fn(**args)
    print(r)


def main():
    arg = parse_remaining(args.arg)
    is_key_query = False
    if arg == None:
        is_key_query = True
    find_chainlib_modules(fltr=[args.module], cmd=args.command, args=arg, handler=default_handler, is_key_query=is_key_query)


if __name__ == '__main__':
    main()
