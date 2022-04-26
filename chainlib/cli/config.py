# standard imports
import logging
import os
import sys
import stat

# external imports
import confini

# local imports
from .base import (
        Flag,
        default_config_dir as default_parent_config_dir,
        )

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


    @staticmethod
    def override_defaults(base_dir=None, default_fee_limit=None):
        if base_dir != None:
            Config.default_base_config_dir = os.path.realpath(base_dir)
        if default_fee_limit != None:
            Config.default_fee_limit = int(default_fee_limit)


    @classmethod
    def from_args(cls, args, arg_flags=0x0f, env=os.environ, extra_args={}, base_config_dir=None, default_config_dir=None, user_config_dir=None, default_fee_limit=None, logger=None, load_callback=None, dump_writer=sys.stdout):
        """Parses arguments in argparse.ArgumentParser instance, then match and override configuration values that match them.

        The method processes all known argument flags from chainlib.cli.Flag passed in the "args" argument. 

        All entries in extra_args may be used to associate arguments not defined in the argument flags with configuration variables, in the following manner:

        - The value of argparser.ArgumentParser instance attribute with the dictionary key string is looked up.
        - If the value is None (defined but empty), any existing value for the configuration directive will be kept.
        - If the value of the extra_args dictionary entry is None, then the value will be stored in the configuration under the upper-case value of the key string, prefixed with "_" ("foo_bar" becomes "_FOO_BAR")
        - If the value of the extra_args dictionary entries is a string, then the value will be stored in the configuration under that literal string.
 
        Missing attributes defined by both the "args" and "extra_args" arguments will both raise an AttributeError.

        The python package "confini" is used to process and render the configuration.

        The confini config schema is determined in the following manner:

        - If nothing is set, only the config folder in chainlib.data.config will be used as schema.
        - If base_config_dir is a string or list, the config directives from the path(s) will be added to the schema.

        The global override config directories are determined in the following manner:

        - If no default_config_dir is defined, the environment variable CONFINI_DIR will be used.
        - If default_config_dir is a string or list, values from the config directives from the path(s) will override those defined in the schema(s).

        The user override config directories work the same way as the global ones, but the namespace - if defined - are dependent on them. They are only applied if the CONFIG arg flag is set. User override config directories are determined in the following manner:

        - If --config argument is not defined and the pyxdg module is present, the first available xdg basedir is used.
        - If --config argument is defined, the directory defined by its value will be used.

        The namespace, if defined, will be stored under the CONFIG_USER_NAMESPACE configuration key.

        :param args: Argument parser object
        :type args: argparse.ArgumentParser
        :param arg_flags: Argument flags defining which arguments to process into configuration.
        :type arg_flags: confini.cli.args.ArgumentParser
        :param env: Environment variables selection
        :type env: dict
        :param extra_args: Extra arguments to process and override.
        :type extra_args: dict
        :param base_config_dir: Path(s) to one or more directories extending the base chainlib config schema.
        :type base_config_dir: list or str
        :param default_config_dir: Path(s) to one or more directories overriding the defaults defined in the schema config directories.
        :type default_config_dir: list or str
        :param user_config_dir: User xdg config basedir, with namespace
        :type user_config_dir: str
        :param default_fee_limit: Default value for fee limit argument
        :type default_fee_limit: int
        :param logger: Logger instance to use during argument processing (will use package namespace logger if None)
        :type logger: logging.Logger
        :param load_callback: Callback receiving config instance as argument after config processing and load completes.
        :type load_callback: function
        :raises AttributeError: Attribute defined in flag not found in parsed arguments
        :rtype: confini.Config
        :return: Processed configuation
        """
        env_prefix = getattr(args, 'env_prefix', None)
        env_prefix_str = env_prefix
        if env_prefix_str == None:
            env_prefix_str = ''
        else:
            env_prefix_str += '_'

        env_loglevel_key_str = env_prefix_str + 'LOGLEVEL'
        env_loglevel = os.environ.get(env_loglevel_key_str)

        if logger == None:
            logger = logging.getLogger()

        if env_loglevel != None:
            env_loglevel = env_loglevel.lower()
            if env_loglevel == '0' or env_loglevel == 'no' or env_loglevel == 'none' or env_loglevel == 'disable' or env_loglevel == 'disabled' or env_loglevel == 'off':
                logging.disable()
            elif env_loglevel == '1' or env_loglevel == 'err' or env_loglevel == 'error':
                logger.setLevel(logging.ERROR)
            elif env_loglevel == '2' or env_loglevel == 'warning' or env_loglevel == 'warn':
                logger.setLevel(logging.WARNING)
            elif env_loglevel == '3' or env_loglevel == 'info':
                logger.setLevel(logging.INFO)
            else:
                valid_level = False
                try:
                    num_loglevel = int(env_loglevel)
                    valid_level = True
                except:
                    if env_loglevel == 'debug':
                        valid_level = True

                if not valid_level:
                    raise ValueError('unknown loglevel {} set in environment variable {}'.format(env_loglevel, env_loglevel_key_str))

                logger.setLevel(logging.DEBUG)


        if arg_flags & Flag.VERBOSE:
            if args.vv:
                logger.setLevel(logging.DEBUG)
            elif args.v:
                logger.setLevel(logging.INFO)
            if args.no_logs:
                logging.disable()
   
        override_config_dirs = []
        config_dir = [cls.default_base_config_dir]

        if user_config_dir == None:
            try:
                import xdg.BaseDirectory
                user_config_dir = xdg.BaseDirectory.load_first_config('chainlib/eth')
            except ModuleNotFoundError:
                pass

        # if one or more additional base dirs are defined, add these after the default base dir
        # the consecutive dirs cannot include duplicate sections
        if base_config_dir != None:
            logg.debug('have explicit base config addition {}'.format(base_config_dir))
            if isinstance(base_config_dir, str):
                base_config_dir = [base_config_dir]
            for d in base_config_dir:
                config_dir.append(d)
            logg.debug('processing config dir {}'.format(config_dir))

        # confini dir env var will be used for override configs only in this case
        if default_config_dir == None:
            default_config_dir = env.get('CONFINI_DIR')
        if default_config_dir != None:
            if isinstance(default_config_dir, str):
                default_config_dir = [default_config_dir]
            for d in default_config_dir:
                override_config_dirs.append(d)

        # process config command line arguments
        if arg_flags & Flag.CONFIG:
            effective_user_config_dir = getattr(args, 'config', None)
            if effective_user_config_dir == None:
                effective_user_config_dir = user_config_dir
            if effective_user_config_dir != None:
                if getattr(args, 'namespace', None) != None:
                    effective_user_config_dir = os.path.join(effective_user_config_dir, args.namespace)
                #if config_dir == None:
                #    config_dir = [cls.default_base_config_dir, effective_user_config_dir]
                #    logg.debug('using config arg as base config addition {}'.format(effective_user_config_dir))
                #else:
                override_config_dirs.append(effective_user_config_dir)
                logg.debug('using config arg as config override {}'.format(effective_user_config_dir))

        #if config_dir == None:
        #    if default_config_dir == None:
        #        default_config_dir = default_parent_config_dir
        #    config_dir = default_config_dir
        #    override_config_dirs = []

        config = confini.Config(config_dir, env_prefix=env_prefix, override_dirs=override_config_dirs)
        config.process()

        config.add(getattr(args, 'raw'), '_RAW')

        args_override = {}
   
        if arg_flags & Flag.PROVIDER:
            args_override['RPC_PROVIDER'] = getattr(args, 'p')
            args_override['RPC_DIALECT'] = getattr(args, 'rpc_dialect')
        if arg_flags & Flag.CHAIN_SPEC:
            args_override['CHAIN_SPEC'] = getattr(args, 'i')
        if arg_flags & Flag.KEY_FILE:
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
        config.dict_override(args_override, 'cli args', allow_empty=True)

        if arg_flags & (Flag.PROVIDER | Flag.NO_TARGET) == Flag.PROVIDER:
            config.add(getattr(args, 'height'), '_HEIGHT')
        if arg_flags & Flag.UNSAFE:
            config.add(getattr(args, 'u'), '_UNSAFE')
        if arg_flags & (Flag.SIGN | Flag.FEE):
            config.add(getattr(args, 'fee_price'), '_FEE_PRICE')
            fee_limit = getattr(args, 'fee_limit')
            if fee_limit == None:
                fee_limit = default_fee_limit
            if fee_limit == None:
                fee_limit = cls.default_fee_limit
            config.add(fee_limit, '_FEE_LIMIT')
        if arg_flags & (Flag.SIGN | Flag.NONCE):
            config.add(getattr(args, 'nonce'), '_NONCE')

        if arg_flags & Flag.SIGN:
            config.add(getattr(args, 's'), '_RPC_SEND')

            # handle wait
            wait = 0
            if args.w:
                wait |= Flag.WAIT
            if args.ww:
                wait |= Flag.WAIT_ALL
            wait_last = wait & (Flag.WAIT | Flag.WAIT_ALL)
            config.add(bool(wait_last), '_WAIT')
            wait_all = wait & Flag.WAIT_ALL
            config.add(bool(wait_all), '_WAIT_ALL')


        if arg_flags & Flag.SEQ:
            config.add(getattr(args, 'seq'), '_SEQ')
        if arg_flags & Flag.WALLET:
            config.add(getattr(args, 'recipient'), '_RECIPIENT')
        if arg_flags & Flag.EXEC:
            config.add(getattr(args, 'executable_address'), '_EXEC_ADDRESS')

        if arg_flags & Flag.CONFIG:
            config.add(getattr(args, 'namespace'), 'CONFIG_USER_NAMESPACE')

        if arg_flags & Flag.RPC_AUTH:
            config.add(getattr(args, 'rpc_auth'), 'RPC_AUTH')
            config.add(getattr(args, 'rpc_credentials'), 'RPC_CREDENTIALS')

        for k in extra_args.keys():
            logg.debug('extra_agrs {}'.format(k))
            v = extra_args[k]
            if v == None:
                v = '_' + k.upper()
            r =  getattr(args, k)
            existing_r = None
            try:
                existing_r = config.get(v)
            except KeyError:
                pass
            if existing_r == None or r != None:
                config.add(r, v, exists_ok=True)
                logg.debug('added {} to {}'.format(r, v))

        if getattr(args, 'dumpconfig', None):
            if args.dumpconfig == 'ini':
                from confini.export import ConfigExporter
                exporter = ConfigExporter(config, target=sys.stdout, doc=False)
                exporter.export(exclude_sections=['config'])
            elif args.dumpconfig == 'env':
                from confini.env import export_env
                export_env(config)

#            config_keys = config.all()
#            with_values = not config.get('_RAW')
#            for k in config_keys:
#                if k[0] == '_':
#                    continue
#                s = k + '='
#                if with_values:
#                    v = config.get(k)
#                    if v != None:
#                        s += str(v)
#                s += '\n'
#                dump_writer.write(s)
            sys.exit(0)

        if load_callback != None:
            load_callback(config)

        return config
