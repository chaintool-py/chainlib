# standard imports
import argparse
import sys
import os
import logging

# local imports
from chainlib.cli.find import find_chainlib_modules

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()


ap = argparse.ArgumentParser()
ap.add_argument('--cmd', type=str, help='command to execute on module. default command will be executed if not specified')
ap.add_argument('--arg', type=str, action='append', help='argument for command to execute')
ap.add_argument('-v', action='store_true', help='verbose logging')
ap.add_argument('-vv', action='store_true', help='very verbose logging')
ap.add_argument('module', type=str, help='module to locate and execute')
args = ap.parse_args(sys.argv[1:])

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)


def default_handler(m, cmd, args):
    r = None
    if cmd == None:
        if args == None:
            r = m.default()
        else:
            r = m.default(*args)
    else:
        fn = getattr(m, cmd)
        if args == None:
            r = fn()
        else:
            r = fn(*args)
    print(r)


def main():
    find_chainlib_modules(fltr=[args.module], cmd=args.cmd, args=args.arg, handler=default_handler)


if __name__ == '__main__':
    main()
