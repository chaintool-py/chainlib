# standard imports
import argparse
import sys
import os
import logging

# local imports
from chainlib.cli.gen import find_chainlib_modules

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

MODE_GEN = 0
MODE_KEYS = 1
MODE_LS = 2

ap = argparse.ArgumentParser()
ap.add_argument('-v', action='store_true', help='verbose logging')
ap.add_argument('-vv', action='store_true', help='very verbose logging')
ap.add_argument('-k', action='store_true', help='return keys for command')
ap.add_argument('-l', action='store_true', help='list chainlib modules')
ap.add_argument('module', type=str, nargs='?', help='module to locate and execute')
ap.add_argument('command', type=str, nargs='?', help='command to execute on module. default command will be executed if not specified')
ap.add_argument('arg', type=str, nargs=argparse.REMAINDER)
args = ap.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

mode = MODE_GEN
if args.l:
    mode = MODE_LS
elif args.k:
    mode = MODE_KEYS

def parse_remaining(rargs):
    rargsr = []
    debug_lvl = logging.WARNING
    for v in rargs:
        if v == '--help':
            global ap
            ap.print_help()
            sys.exit(0)
        if v == '-vv':
            if debug_lvl > logging.DEBUG:
                debug_lvl = logging.DEBUG
            logg.setLevel(debug_lvl)
            continue
        elif v == '-v':
            if debug_lvl > logging.INFO:
                debug_lvl = logging.INFO
            logg.setLevel(debug_lvl)
            continue
        if v == '-l':
            return (MODE_LS, [],)
        elif v == '-k':
            return (MODE_KEYS, [],)
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
    return (MODE_GEN, r,)


def list_handler(m, cmd, args, is_key_query=False):
    print(m.__name__)


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
    global mode
    (parsed_mode, arg) = parse_remaining(args.arg)
    if parsed_mode > mode:
        mode = parsed_mode
    logg.debug('running mode: ' + str(mode))
    is_key_query = False
    hndlr = default_handler
    cmd = None
    module = None
    if mode == MODE_LS:
        hndlr = list_handler
    else:
        module = [args.module]
        cmd = args.command
        if mode == MODE_KEYS:
            if cmd == None:
                raise ValueError('command required for key query')
            is_key_query = True

    find_chainlib_modules(fltr=module, cmd=args.command, args=arg, handler=hndlr, is_key_query=is_key_query)


if __name__ == '__main__':
    main()
