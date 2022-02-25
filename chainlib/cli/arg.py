# standard imports
import logging
import argparse
import enum
import os
import select
import sys
import re

# local imports
from .base import (
        default_config_dir,
        Flag,
        argflag_std_target,
        )

logg = logging.getLogger(__name__)


def stdin_arg():
    """Retreive input arguments from stdin if they exist.

    Method does not block, and expects arguments to be ready on stdin before being called.

    :rtype: str
    :returns: Input arguments string
    """
    h = select.select([sys.stdin], [], [], 0)
    if len(h[0]) > 0:
        v = h[0][0].read()
        return v.rstrip()
    return None

_default_long_args = {
        '-a': '--recipient',
        '-e': '--executable-address',
        '-s': '--send',
        '-y': '--key-file',
                }

_default_dest = {
        '-a': 'recipient',
        '-e': 'executable_address',
        }


_default_fmt = 'human'


class ArgumentParser(argparse.ArgumentParser):
    """Extends the standard library argument parser to construct arguments based on configuration flags.

    The extended class is set up to facilitate piping of single positional arguments via stdin. For this reason, positional arguments should be added using the locally defined add_positional method instead of add_argument.

    Long flag aliases for short flags are editable using the arg_long argument. Editing a non-existent short flag will produce no error and have no effect. Adding a long flag for a short flag that does not have an alias will also not have effect.

    Calls chainlib.cli.args.ArgumentParser.process_flags with arg_flags and env arguments, see the method's documentation for further details.

    :param arg_flags: Argument flag bit vector to generate configuration values for.
    :type arg_flags: chainlib.cli.Flag
    :param arg_long: Change long flag alias for given short flags. Example value: {'-a': '--addr', '-e': '--contract'}
    :type arg_long: dict
    :param env: Environment variables
    :type env: dict
    :param usage: Usage string, passed to parent
    :type usage: str
    :param description: Description string, passed to parent
    :type description: str
    :param epilog: Epilog string, passed to parent
    :type epilog: str
    """

    def __init__(self, arg_flags=0x0f, arg_long={}, env=os.environ, usage=None, description=None, epilog=None, default_format=_default_fmt, *args, **kwargs):
        super(ArgumentParser, self).__init__(usage=usage, description=description, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter, *args, **kwargs)
    
        self.pos_args = []
        self.long_args = _default_long_args
        self.arg_dest = _default_dest
        self.default_format = default_format

        re_long = r'^--[a-z\-]+$'
        for k in arg_long.keys():
            if re.match(re_long, arg_long[k]) == None:
                raise ValueError('invalid long arg {}'.format(arg_long[k]))
            self.long_args[k] = arg_long[k]
            dest = arg_long[k][2:]
            dest = dest.replace('-', '_')
            self.arg_dest[k] = dest

        self.process_flags(arg_flags, env)


    def add_positional(self, name, type=str, help=None, append=False, required=True):
        """Add a positional argument.

        Stdin piping will only be possible in the event a single positional argument is defined.

        If the "required" is set, the resulting parsed arguments must have provided a value either from stdin or excplicitly on the command line.

        :param name: Attribute name of argument
        :type name: str
        :param type: Argument type
        :type type: str
        :param help: Help string
        :type help: str
        :param required: If true, argument will be set to required
        :type required: bool
        """
        self.pos_args.append((name, type, help, required, append,))


    def parse_args(self, argv=sys.argv[1:]):
        """Overrides the argparse.ArgumentParser.parse_args method.

        Implements reading arguments from stdin if a single positional argument is defined (and not set to required).

        If the "required" was set for the single positional argument, the resulting parsed arguments must have provided a value either from stdin or excplicitly on the command line.

        :param argv: Argument vector to process
        :type argv: list
        """
        if len(self.pos_args) == 1:
            arg = self.pos_args[0]
            if arg[4]:
                self.add_argument(arg[0], nargs='*', type=arg[1], default=stdin_arg(), help=arg[2])
            else:
                self.add_argument(arg[0], nargs='?', type=arg[1], default=stdin_arg(), help=arg[2])
        else:
            for arg in self.pos_args:
                if arg[3]:
                    if arg[4]:
                        self.add_argument(arg[0], nargs='+', type=arg[1], help=arg[2])
                    else:
                        self.add_argument(arg[0], type=arg[1], help=arg[2])
                else:
                    if arg[4]:
                        self.add_argument(arg[0], nargs='*', type=arg[1], help=arg[2])
                    else:
                        self.add_argument(arg[0], type=arg[1], help=arg[2])
        args = super(ArgumentParser, self).parse_args(args=argv)

        if getattr(args, 'dumpconfig', None) != None:
            return args

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
        """Configures the arguments of the parser using the provided flags.

        Environment variables are used for default values for:

        CONFINI_DIR: -c, --config 
        CONFINI_ENV_PREFIX: --env-prefix
        
        This method is called by the constructor, and is not intended to be called directly.

        :param arg_flags: Argument flag bit vector to generate configuration values for.
        :type arg_flags: chainlib.cli.Flag
        :param env: Environment variables
        :type env: dict
        """
        if arg_flags & Flag.VERBOSE:
            self.add_argument('--no-logs', dest='no_logs',action='store_true', help='Turn off all logging')
            self.add_argument('-v', action='store_true', help='Be verbose')
            self.add_argument('-vv', action='store_true', help='Be more verbose')
        if arg_flags & Flag.CONFIG:
            self.add_argument('-c', '--config', type=str, default=env.get('CONFINI_DIR'), help='Configuration directory')
            self.add_argument('-n', '--namespace', type=str, help='Configuration namespace')
            self.add_argument('--dumpconfig', type=str, choices=['env', 'ini'], help='Output configuration and quit. Use with --raw to omit values and output schema only.')
        if arg_flags & Flag.WAIT:
            self.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
            self.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
        if arg_flags & Flag.ENV_PREFIX:
            self.add_argument('--env-prefix', default=env.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
        if arg_flags & Flag.PROVIDER:
            self.add_argument('-p', '--rpc-provider', dest='p', type=str, help='RPC HTTP(S) provider url')
            self.add_argument('--rpc-dialect', dest='rpc_dialect', type=str, help='RPC HTTP(S) backend dialect')
            if arg_flags & Flag.NO_TARGET == 0:
                self.add_argument('--height', default='latest', help='Block height to execute against')
            if arg_flags & Flag.RPC_AUTH:
                self.add_argument('--rpc-auth', dest='rpc_auth', type=str, help='RPC autentication scheme')
                self.add_argument('--rpc-credentials', dest='rpc_credentials', type=str, help='RPC autentication credential values')
        if arg_flags & Flag.CHAIN_SPEC:
            self.add_argument('-i', '--chain-spec', dest='i', type=str, help='Chain specification string')
        if arg_flags & Flag.UNSAFE:
            self.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Do not verify address checksums')
        if arg_flags & Flag.SEQ:
            self.add_argument('--seq', action='store_true', help='Use sequential rpc ids')
        if arg_flags & Flag.KEY_FILE:
            self.add_argument('-y', self.long_args['-y'], dest='y', type=str, help='Keystore file to use for signing or address')
            self.add_argument('--passphrase-file', dest='passphrase_file', type=str, help='File containing passphrase for keystore')
        if arg_flags & Flag.SEND:
            self.add_argument('-s', self.long_args['-s'], dest='s', action='store_true', help='Send to network')
        if arg_flags & Flag.RAW:
            self.add_argument('--raw', action='store_true', help='Do not decode output')
        if arg_flags & (Flag.SIGN | Flag.NONCE):
            self.add_argument('--nonce', type=int, help='override nonce')
        if arg_flags & (Flag.SIGN | Flag.FEE):
            self.add_argument('--fee-price', dest='fee_price', type=int, help='override fee price')
            self.add_argument('--fee-limit', dest='fee_limit', type=int, help='override fee limit')
        # wtf?
        #if arg_flags & argflag_std_target == 0:
        #    arg_flags |= Flag.WALLET
        if arg_flags & Flag.EXEC:
            self.add_argument('-e', self.long_args['-e'], dest=self.arg_dest['-e'], type=str, help='contract address')
        if arg_flags & Flag.WALLET:
            self.add_argument('-a', self.long_args['-a'], dest=self.arg_dest['-a'], type=str, help='recipient address')
        if arg_flags & (Flag.FMT_HUMAN | Flag.FMT_WIRE | Flag.FMT_RPC):
            format_choices = []
            if arg_flags & Flag.FMT_HUMAN:
                format_choices.append('human')
            if arg_flags & Flag.FMT_WIRE:
                format_choices.append('bin')
            if arg_flags & Flag.FMT_RPC:
                format_choices.append('rpc')
            self.add_argument('-f', '--format', type=str, choices=format_choices, help='output formatting (default: {})'.format(self.default_format))
