# standard imports
import logging
import os

# external imports
import confini

# local imports
from .base import (
        Flag,
        default_config_dir as default_parent_config_dir,
        )

#logg = logging.getLogger(__name__)
logg = logging.getLogger()


def logcallback(config):
    logg.debug('config loaded:\n{}'.format(config))


class Config(confini.Config):

    default_base_config_dir = default_parent_config_dir
    default_fee_limit = 0

    @classmethod
    def from_args(cls, args, arg_flags, extra_args={}, base_config_dir=None, default_config_dir=None, user_config_dir=None, default_fee_limit=None, logger=None, load_callback=logcallback):

        if logger == None:
            logger = logging.getLogger()

        if arg_flags & Flag.CONFIG:
            if args.vv:
                logger.setLevel(logging.DEBUG)
            elif args.v:
                logger.setLevel(logging.INFO)
   
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
            default_config_dir = os.environ.get('CONFINI_DIR')
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
                if config_dir == None:
                    if getattr(args, 'namespace', None) != None:
                        arg_config_dir = os.path.join(effective_user_config_dir, args.namespace)
                    config_dir = [cls.default_base_config_dir, effective_user_config_dir]
                    logg.debug('using config arg as base config addition {}'.format(effective_user_config_dir))
                else:
                    if getattr(args, 'namespace', None) != None:
                        arg_config_dir = os.path.join(effective_user_config_dir, args.namespace)
                    override_config_dirs.append(effective_user_config_dir)
                    logg.debug('using config arg as config override {}'.format(effective_user_config_dir))


        if config_dir == None:
            if default_config_dir == None:
                default_config_dir = default_parent_config_dir
            config_dir = default_config_dir
            override_config_dirs = []
        env_prefix = getattr(args, 'env_prefix', None)

        config = confini.Config(config_dir, env_prefix=args.env_prefix, override_dirs=override_config_dirs)
        config.process()

        args_override = {}

        if arg_flags & Flag.PROVIDER:
            args_override['RPC_HTTP_PROVIDER'] = getattr(args, 'p')
        if arg_flags & Flag.CHAIN_SPEC:
            args_override['CHAIN_SPEC'] = getattr(args, 'i')
        if arg_flags & Flag.KEY_FILE:
            args_override['WALLET_KEY_FILE'] = getattr(args, 'y')
       
        config.dict_override(args_override, 'cli args')

        if arg_flags & Flag.PROVIDER:
            config.add(getattr(args, 'height'), '_HEIGHT')
        if arg_flags & Flag.UNSAFE:
            config.add(getattr(args, 'u'), '_UNSAFE')
        if arg_flags & Flag.SEND:
            fee_limit = getattr(args, 'fee_limit')
            if fee_limit == None:
                fee_limit = default_fee_limit
            if fee_limit == None:
                fee_limit = cls.default_fee_limit
            config.add(fee_limit, '_FEE_LIMIT')
            config.add(getattr(args, 'fee_price'), '_FEE_PRICE')
            config.add(getattr(args, 'nonce'), '_NONCE')
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

        config.add(getattr(args, 'raw'), '_RAW')

        for k in extra_args.keys():
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

        if load_callback != None:
            load_callback(config)

        return config
