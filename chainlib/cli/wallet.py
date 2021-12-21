# standard imports
import logging

logg = logging.getLogger(__name__)


class Wallet:
    """Provides a unified wallet factory for both read and write operations, and a convenience instantiator using rendered configurations from chainlib.cli.config.Config

    :param signer_cls: Class to use for signer instantiation
    :type signer_cls: TODO - define signer interface in chainlib
    :param keystore: Keystore object
    :type keystore: TODO - define keystore interface in chainlib
    :param checksummer: If define any address returned from instance methods will be checksummed using the given function unless explicitly told otherwise
    :type checksummer: TODO - define checksummer interface in chainlib
    :todo: sign_transaction_to_rlp from chainlib-eth must be renamed to sign_transaction_to_wire, and included as part of signer interface
    """
    
    def __init__(self, signer_cls, keystore=None, checksummer=None):
        self.signer_constructor = signer_cls
        self.keystore = keystore
        self.signer = None
        self.signer_address = None
        self.nonce_oracle = None
        self.gas_oracle = None
        self.checksummer = checksummer
        self.use_checksum = False


    def init(self):
        self.signer = self.signer_constructor(self.keystore)


    def from_config(self, config):
        """Instantiates a signer from the registered signer class, using parameters from a processed configuration.

        Currently only keyfile loader is implemented, and defers processing to chainlib.cli.wallet.Wallet.from_keyfile. The keyfile path is read from the "WALLET_KEY_FILE" value.

        Keyfile passphrase is value of "WALLET_PASSPHRASE" configuration parameter, or empty string by default.

        If the "_UNSAFE" configuration parameter is set to True, address checksumming will be deactivated.

        :param config: Configuration to load wallet with
        :type config: confini.Config
        :rtype: TODO - signer interface
        :returns: Signer
        """
        wallet_keyfile = config.get('WALLET_KEY_FILE')
        if wallet_keyfile:
            logg.debug('keyfile {}'.format(wallet_keyfile))
            self.from_keyfile(wallet_keyfile, passphrase=config.get('WALLET_PASSPHRASE', ''))
        self.use_checksum = not config.true('_UNSAFE')
        return self.signer
       

    def from_keyfile(self, key_file, passphrase=''):
        """Instantiates a signer from the registered signer class, with private key from the given keyfile.

        :param key_file: Keyfile path
        :type key_file: str
        :param passphrase: Private key passphrase
        :type passphrase: str
        :rtype: TODO - signer interface
        :returns: Signer
        """
        logg.debug('importing key from keystore file {}'.format(key_file))
        self.signer_address = self.keystore.import_keystore_file(key_file, password=passphrase)
        self.signer = self.signer_constructor(self.keystore)
        logg.info('key for {} imported from keyfile {}'.format(self.signer_address, key_file))
        return self.signer


    def from_address(self, address):
        """Instantiates a read-only wallet with the given address.

        If checksummer is defined and active, the address argument must be a valid checksum address.

        :param address: Wallet address
        :type address: str
        :raises AttributeError: Checksum requested but no checksummer assigned
        :raises ValueError: Invalid checksum address
        :rtype: str
        :returns: Checksummed address
        """
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
        """Signer interface getter.

        :rtype: TODO - signer interface
        :returns: Signer
        """
        return self.signer


    def get_signer_address(self):
        """Wallet address getter.

        :rtype: str
        :returns: Wallet address
        """
        return self.signer_address
