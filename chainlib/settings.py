# standard imports
import logging

# external imports
from aiee.numbers import postfix_to_int

# local imports
from .chain import ChainSpec

logg = logging.getLogger(__name__)


class ChainSettings:

    def __init__(self):
        self.o = {}
        self.get = self.o.get


    def set(self, k, v):
        self.o[k] = v


    def __str__(self):
        ks = list(self.o.keys())
        ks.sort()
        s = ''
        for k in ks:
            s += '{}: {}\n'.format(k, self.o.get(k))
        return s


def process_settings_dialect(settings, config):
    if config.get('RPC_DIALECT') != 'default':
        import importlib
        m = importlib.import_module(config.get('RPC_DIALECT'))
        settings.set('RPC_DIALECT_FILTER', m.DialectFilter())
    return settings


def process_settings_common(settings, config):
    chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))
    settings.set('CHAIN_SPEC', chain_spec)
    return settings


def process_settings_signer_check(settings, config):
    unsigned_address = None
    try:
        unsigned_address = config.get('_UNSIGNED_SENDER_ADDRESS')
    except KeyError:
        pass
    if config.get('WALLET_KEY_FILE') != None and unsigned_address != None:
        logg.warning('misconfigured client has both wallet key file and signed sender options set')
    return settings


def process_settings_value(settings, config):
    value = None
    try:
        value = config.get('_VALUE')
    except KeyError:
        return settings

    value = postfix_to_int(config.get('_VALUE'))

    settings.set('VALUE', value)
    return settings


def process_settings(settings, config):
    settings = process_settings_common(settings, config)
    settings = process_settings_value(settings, config)
    settings = process_settings_dialect(settings, config)
    settings = process_settings_signer_check(settings, config)
    return settings
