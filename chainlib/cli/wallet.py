# standard imports
import logging

# external imports
from crypto_dev_signer.keystore.dict import DictKeystore

logg = logging.getLogger(__name__)


class Wallet:
    
    def __init__(self, signer_cls, keystore=DictKeystore(), checksummer=None):
        self.signer_constructor = signer_cls
        self.keystore = keystore
        self.signer = None
        self.signer_address = None
        self.nonce_oracle = None
        self.gas_oracle = None
        self.checksummer = checksummer
        self.use_checksum = False


    def from_config(self, config):
        wallet_keyfile = config.get('WALLET_KEY_FILE')
        if wallet_keyfile:
            logg.debug('keyfile {}'.format(wallet_keyfile))
            self.from_keyfile(wallet_keyfile, passphrase=config.get('WALLET_PASSPHRASE', ''))
        self.use_checksum = not config.true('_UNSAFE')
       

    def from_keyfile(self, key_file, passphrase=''):
        logg.debug('importing key from keystore file {}'.format(key_file))
        self.signer_address = self.keystore.import_keystore_file(key_file, password=passphrase)
        self.signer = self.signer_constructor(self.keystore)
        logg.info('key for {} imported from keyfile {}'.format(self.signer_address, key_file))
        return self.signer


    def from_address(self, address):
        self.signer_address = address
        if self.use_checksum:
            if self.checksummer == None:
                raise AttributeError('checksum required but no checksummer assigned')
            if not self.checksummer.valid(self.signer_address):
                raise ValueError('invalid checksum address {}'.format(self.signer_address))
        elif self.checksummer != None:
            self.signer_address = self.checksummer.sum(self.signer_address)
        logg.info('sender_address set to {}'.format(self.signer_address))
        return self.signer_address


    def get_signer(self):
        return self.signer


    def get_signer_address(self):
        return self.signer_address
