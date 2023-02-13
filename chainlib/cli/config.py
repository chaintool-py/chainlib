# standard imports
import logging
import os
import sys
import stat

# external imports
import confini

script_dir = os.path.dirname(os.path.realpath(__file__))
default_parent_config_dir = os.path.join(script_dir, '..', 'data', 'config')

logg = logging.getLogger(__name__)


def logcallback(config):
    """Callback to dump config contents to log after completed config load
    
    :param config: Config object
    :type config: confini.Config
    """
    logg.debug('config loaded:\n{}'.format(config))


class Config(confini.Config):
    """Extends confini.Config.

    Processes argument parser attributes to configuration variables.

    Provides sane configuration overrides and fallbacks.

    """        
    default_base_config_dir = default_parent_config_dir
    default_fee_limit = 0

    def __init__(self, config_dir=None, namespace=None):
        self.namespace = namespace
        if config_dir == None:
            config_dir = self.default_base_config_dir
        if self.namespace != None:
            config_dir = os.path.join(config_dir, namespace)
        super(Config, self).__init__(config_dir)


    def add_user_dir(self, v):
        if self.namespace != None:
            v = os.path.join(v, self.namespace)
        return super(Config, self).add_override_dir(v)


def process_config(config, arg, args, flags, positional_name=None):

    if arg.match('env', flags):
        config.set_env_prefix(getattr(args, 'env_prefix'))

    config.process()

    args_override = {}

    if arg.match('raw', flags):
        config.add(getattr(args, 'r', None), '_RAW')
        config.add(getattr(args, '0', None), '_NOLINE')
 
    if arg.match('provider', flags):
        args_override['RPC_PROVIDER'] = getattr(args, 'p')
        args_override['RPC_DIALECT'] = getattr(args, 'rpc_dialect')

    if arg.match('chain_spec', flags):
        args_override['CHAIN_SPEC'] = getattr(args, 'i')

    if arg.match('config', flags):
        config.add(getattr(args, 'namespace', None), 'CONFIG_USER_NAMESPACE')

    if arg.match('key_file', flags):
        args_override['WALLET_KEY_FILE'] = getattr(args, 'y')
        fp = getattr(args, 'passphrase_file')
        if fp != None:
            st = os.stat(fp)
            if stat.S_IMODE(st.st_mode) & (stat.S_IRWXO | stat.S_IRWXG) > 0:
                logg.warning('others than owner have access on password file')
            f = open(fp, 'r')
            args_override['WALLET_PASSPHRASE'] = f.read()
            f.close()
        config.censor('PASSPHRASE', 'WALLET')

    if arg.match('backend', flags):
        args_override['STATE_BACKEND'] = getattr(args, 'backend')

    if arg.match('path', flags):
        args_override['STATE_PATH'] = getattr(args, 'state_path')

    config.dict_override(args_override, 'cli args', allow_empty=True)

    if arg.match('provider', flags):
        if arg.match('target', flags):
            config.add(getattr(args, 'height'), '_HEIGHT')
    
    if arg.match('unsafe', flags):
        config.add(getattr(args, 'u'), '_UNSAFE')

    if arg.match('sign', flags):
        config.add(getattr(args, 's'), '_RPC_SEND')

        if arg.match('fee', flags):
            config.add(getattr(args, 'fee_price'), '_FEE_PRICE')

        if arg.match('nonce', flags):
            config.add(getattr(args, 'nonce'), '_NONCE')

        if arg.match('wait', flags):
            if args.ww:
                config.add(True, '_WAIT_ALL')
                config.add(True, '_WAIT')
            elif args.w:
                config.add(True, '_WAIT')
 
    if arg.match('fee', flags):
        fee_limit = getattr(args, 'fee_limit')
        if fee_limit == None:
            fee_limit = int(config.get('CHAIN_MIN_FEE'))
        config.add(fee_limit, '_FEE_LIMIT')
   
    if arg.match('seq', flags):
        config.add(getattr(args, 'seq'), '_SEQ')

    if arg.match('wallet', flags):    
        config.add(getattr(args, 'recipient'), '_RECIPIENT')

    if arg.match('value', flags):
        config.add(getattr(args, 'total'), '_TOTAL')

    if arg.match('exec', flags):
        config.add(getattr(args, 'executable_address'), '_EXEC_ADDRESS')

    if arg.match('rpc_auth', flags):
        config.add(getattr(args, 'rpc_auth'), 'RPC_AUTH')
        config.add(getattr(args, 'rpc_credentials'), 'RPC_CREDENTIALS')

    if arg.match('sender', flags):
        config.add(getattr(args, 'f'), '_UNSIGNED_SENDER_ADDRESS')

    if positional_name != None:
        config.add(None, '_POSARG', False)
        pos_arg = getattr(args, positional_name)
        if len(pos_arg) > 0:
            config.add(pos_arg[0], '_POSARG', True)

    if arg.match('tab', flags):
        config.add(args.o, '_OUTARG', False)

    return config
