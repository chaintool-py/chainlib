# standard imports
import logging
import argparse
import enum
import os
import select
import sys

# local imports
from .base import (
        default_config_dir,
        Flag,
        argflag_std_target,
        )

logg = logging.getLogger(__name__)


def stdin_arg():
    h = select.select([sys.stdin], [], [], 0)
    if len(h[0]) > 0:
        v = h[0][0].read()
        return v.rstrip()
    return None


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self, arg_flags=0x0f, env=os.environ, usage=None, description=None, epilog=None, *args, **kwargs):
        super(ArgumentParser, self).__init__(usage=usage, description=description, epilog=epilog)
        self.process_flags(arg_flags, env)
        self.pos_args = []


    def add_positional(self, name, type=str, help=None, required=True):
        self.pos_args.append((name, type, help, required,))


    def parse_args(self, argv=sys.argv[1:]):
        if len(self.pos_args) == 1:
            arg = self.pos_args[0]
            self.add_argument(arg[0], nargs='?', type=arg[1], default=stdin_arg(), help=arg[2])
        else:
            for arg in self.pos_args:
                if arg[3]:
                    self.add_argument(arg[0], type=arg[1], help=arg[2])
                else:
                    self.add_argument(arg[0], nargs='?', type=arg[1], help=arg[2])
        args = super(ArgumentParser, self).parse_args(args=argv)

        if len(self.pos_args) == 1:
            arg = self.pos_args[0]
            argname = arg[0]
            required = arg[3]
            if getattr(args, arg[0], None) == None:
                argp = stdin_arg()
                if argp == None and required:
                    self.error('need first positional argument or value from stdin')
                setattr(args, arg[0], argp)

        return args


    def process_flags(self, arg_flags, env):
        if arg_flags & Flag.VERBOSE:
            self.add_argument('-v', action='store_true', help='Be verbose')
            self.add_argument('-vv', action='store_true', help='Be more verbose')
        if arg_flags & Flag.CONFIG:
            self.add_argument('-c', '--config', type=str, default=env.get('CONFINI_DIR'), help='Configuration directory')
            self.add_argument('-n', '--namespace', type=str, help='Configuration namespace')
        if arg_flags & Flag.WAIT:
            self.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
            self.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
        if arg_flags & Flag.ENV_PREFIX:
            self.add_argument('--env-prefix', default=env.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
        if arg_flags & Flag.PROVIDER:
            self.add_argument('-p', '--provider', dest='p', type=str, help='RPC HTTP(S) provider url')
            self.add_argument('--height', default='latest', help='Block height to execute against')
        if arg_flags & Flag.CHAIN_SPEC:
            self.add_argument('-i', '--chain-spec', dest='i', type=str, help='Chain specification string')
        if arg_flags & Flag.UNSAFE:
            self.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Do not verify address checksums')
        if arg_flags & Flag.SEQ:
            self.add_argument('--seq', action='store_true', help='Use sequential rpc ids')
        if arg_flags & Flag.KEY_FILE:
            self.add_argument('-y', '--key-file', dest='y', type=str, help='Keystore file to use for signing or address')
        if arg_flags & Flag.SEND:
            self.add_argument('-s', '--send', dest='s', action='store_true', help='Send to network')
        if arg_flags & Flag.RAW:
            self.add_argument('--raw', action='store_true', help='Do not decode output')
        if arg_flags & Flag.SIGN:
            self.add_argument('--nonce', type=int, help='override nonce')
            self.add_argument('--fee-price', dest='fee_price', type=int, help='override fee price')
            self.add_argument('--fee-limit', dest='fee_limit', type=int, help='override fee limit')
        if arg_flags & argflag_std_target == 0:
            arg_flags |= Flag.WALLET
        if arg_flags & Flag.EXEC:
            self.add_argument('-e', '--exectuable-address', dest='executable_address', type=str, help='contract address')
        if arg_flags & Flag.WALLET:
            self.add_argument('-a', '--recipient', dest='recipient', type=str, help='recipient address')

