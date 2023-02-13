# standard imports
import logging
import argparse #import enum
import select
import sys

# external imports 
from aiee.arg import (
        ArgFlag as BaseArgFlag,
        Arg as BaseArg,
        process_args,
        )

logg = logging.getLogger(__name__)


def stdin_arg():
    """Retreive input arguments from stdin if they exist.

    Method does not block, and expects arguments to be ready on stdin before being called.

    :rtype: str
    :returns: Input arguments string
    """
    h = select.select([sys.stdin], [], [])
    if len(h[0]) > 0:
        v = h[0][0].read()
        return v.rstrip()
    return None


class ArgumentParser(argparse.ArgumentParser):

    def parse_args(self, argv=sys.argv[1:]):
        if '--dumpconfig' in argv:
            argv = [argv[0], '--dumpconfig']
        arg = super(ArgumentParser, self).parse_args(args=argv)
        return arg


    def add_argument(self, *args, **kwargs):
        if args[0][0] != '-':
            kwargs['nargs'] = '*'
        super(ArgumentParser, self).add_argument(*args, **kwargs)


class ArgFlag(BaseArgFlag):

    def __init__(self):
        super(ArgFlag, self).__init__()

        self.add('verbose')
        self.add('config')
        self.add('raw')
        self.add('env')
        self.add('provider')
        self.add('chain_spec')
        self.add('target')
        self.add('unsafe')
        self.add('seq')
        self.add('key_file')
        self.add('fee')
        self.add('nonce')
        self.add('no_target')
        self.add('exec')
        self.add('wallet')
        self.add('wait')
        self.add('wait_all')
        self.add('send')
        self.add('rpc_auth')
        self.add('fmt_human')
        self.add('fmt_wire')
        self.add('fmt_rpc')
        self.add('veryverbose')
        self.add('path')
        self.add('backend')
        self.add('value')
        self.add('tab')
        self.add('sender')

        self.alias('sign', 'key_file', 'send')
        self.alias('std_base', 'verbose', 'config', 'raw', 'env', 'target')
        self.alias('std_base_read', 'unsafe', 'verbose', 'config', 'raw', 'env', 'provider', 'chain_spec', 'seq')
        self.alias('std_read', 'std_base', 'provider', 'chain_spec', 'unsafe', 'seq', 'fee', 'target', 'sign', 'sender')
        self.alias('std_read_noex', 'std_base', 'provider', 'chain_spec', 'seq', 'target')
        self.alias('std_write', 'verbose', 'config', 'raw', 'env', 'provider', 'chain_spec', 'unsafe', 'seq', 'key_file', 'sign', 'target', 'wait', 'wait_all', 'send', 'rpc_auth', 'nonce', 'fee')
        self.alias('std_target', 'no_target', 'exec', 'wallet')
        self.alias('state', 'backend', 'path')

class Arg(BaseArg):
    
    def __init__(self, flags):
        super(Arg, self).__init__(flags)
        self.add_long('no-logs', 'verbose', typ=bool, help='Turn off all logging')
        self.add('v', 'verbose', typ=bool, help='Be verbose')
        self.add('vv', 'verbose', check=False, typ=bool, help='Be more verbose')
        self.add('vvv', 'veryverbose', check=False, typ=bool, help='Be morse verbose with custom tracing')

        self.add('n', 'config', help='Configuration namespace')
        self.set_long('n', 'namespace', dest='namespace')
        self.add('c', 'config', dest='config', help='Configuration directory')
        self.set_long('c', 'config')
        self.add_long('dumpconfig', 'config', help='Output configuration and quit. Use with --raw to omit values and output schema only.')

        self.add('a', 'wallet', dest='recipient', help='Recipient address')
        self.set_long('a', 'recipient')

        self.add('e', 'exec', dest='executable_address', help='Recipient address')
        self.set_long('e', 'executable')

        self.add('w', 'wait', typ=bool, help='Wait for the last transaction to be confirmed')
        self.add('ww', 'wait', check=False, typ=bool, help='Wait for every transaction to be confirmed')

        self.add_long('env-prefix', 'env', help='environment prefix for variables to overwrite configuration')
        
        self.add('p', 'provider', help='RPC HTTP(S) provider url')
        self.set_long('p', 'provider')
        self.add_long('rpc-dialect', 'provider', help='RPC HTTP(S) backend dialect')
        self.add_long('rpc-timeout', 'provider',  help='RPC autentication credential values')
        self.add_long('rpc-proxy', 'provider',  help='RPC autentication credential values')

        self.add_long('height', 'target', default='latest', help='Block height to execute against')
        
        self.add_long('rpc-auth', 'rpc_auth', help='RPC autentication scheme')
        self.add_long('rpc-credentials', 'rpc_auth',  help='RPC autentication credential values')

        self.add('i', 'chain_spec', help='Chain specification string')
        self.set_long('i', 'chain-spec')

        self.add('u', 'unsafe', typ=bool, help='Do not verify address checksums')
        self.set_long('u', 'unsafe')

        self.add_long('seq', 'seq', typ=bool, help='Use sequential rpc ids')

        self.add('y', 'key_file', help='Keystore file to use for signing or address')
        self.set_long('y', 'key_file')
        self.add_long('passphrase-file', 'key_file', help='Keystore file to use for signing or address')

        self.add('s', 'send', typ=bool, help='Send to network')
        self.set_long('s', 'send')

        self.add('f', 'sender', type=str, help='Unsigned sender')
        self.set_long('f', 'from')

        self.add('r', 'raw', typ=bool, help='Do not decode output')
        self.set_long('r', 'raw')
        self.add('0', 'raw', typ=bool, help='Omit newline to output')

        self.add_long('nonce', 'nonce', typ=int, help='override nonce')
        self.add_long('fee-price', 'fee', typ=int, help='override fee price')
        self.add_long('fee-limit', 'fee', typ=int, help='override fee limit')

        self.add_long('total', 'value', typ=bool, help='Deduct calculated fee from value')

        self.add_long('state-path', 'path', help='Path to store state data under')
        self.add_long('runtime-path', 'path', help='Path to store volatile data under')
        self.add_long('backend', 'backend', help='Backend to use for data storage')

        self.add('o', 'tab', typ=str, action='append', help='Include output by key name')
        self.set_long('o', 'output-key')
