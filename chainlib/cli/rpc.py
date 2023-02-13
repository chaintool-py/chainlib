# standard imports
import logging

# external imports
from chainlib.chain import ChainSpec
from chainlib.connection import RPCConnection
from chainlib.jsonrpc import IntSequenceGenerator
from chainlib.nonce import NonceOracle
from chainlib.fee import FeeOracle
from chainlib.error import SignerMissingException

logg = logging.getLogger(__name__)


class Rpc:
    """Convenience wrapper to build rpc connection from processed configuration values.

    :param cls: RPC connection class to instantiate
    :type cls: chainlib.connection.RPCConnection implementation
    :param wallet: Add wallet backend to instance
    :type wallet: chainlib.cli.wallet.Wallet
    """

    default_sender_address = None
    
    def __init__(self, cls, wallet=None):
        self.constructor = cls
        self.id_generator = None
        self.conn = None
        self.chain_spec = None
        self.wallet = wallet
        self.nonce_oracle = None
        self.fee_oracle = None
        self.error_parser = None
        self.sender_address = self.default_sender_address


    def connect_by_config(self, config):
        """Create a connection using the provided configuration, as rendered by chainlib.cli.config.Config.

        The connection url string is fetched from the "RPC_HTTP_PROVIDER" configuration key. Currently only HTTP connection is supported. Basic HTTP auth is supported using the "RPC_HTTP_USERNAME" and "RPC_HTTP_PASSWORD" keys together with "RPC_HTTP_AUTHENTICATION" set to "basic".

        The "CHAIN_SPEC" value is used for the chain context of the connection.

        If the sequence flag was set in the configuration (which generates the configuration key "_SEQ"), a sequential integer generator will be used for rpc ids. Otherwise uuids will be used.


        :param config: Processed configuration 
        :type config: confini.Config
        :rtype: chainlib.connection.RPCConnection
        :returns: An established rpc connection
        """
        if config.get('RPC_SCHEME') != 'http':
            raise NotImplementedError('Only http(s) scheme is implemented for RPC connections at this time')

        auth = None
        if config.get('RPC_AUTH') == 'basic':
            from chainlib.auth import BasicAuth
            auth_parts = config.get('RPC_CREDENTIALS').split(':')
            auth = BasicAuth(auth_parts[0], auth_parts[1])
            logg.debug('using basic http auth')
        
        if config.get('_SEQ'):
            self.id_generator = IntSequenceGenerator()

        self.chain_spec = config.get('CHAIN_SPEC')
        self.conn = self.constructor(url=config.get('RPC_PROVIDER'), chain_spec=self.chain_spec, auth=auth, verify_identity=config.true('RPC_VERIFY'), timeout=float(config.get('RPC_TIMEOUT')))

        if self.wallet.signer != None:
            self.sender_address = self.wallet.signer_address
        elif config.get('_UNSIGNED_SENDER_ADDRESS') != None:
            try:
                self.sender_address = config.get('_UNSIGNED_SENDER_ADDRESS')
            except KeyError:
                pass
            except ValueError:
                pass
        logg.debug('default sender address {} {}'.format(self.default_sender_address, self.sender_address))
    
        return self.conn


    def get_nonce_oracle(self):
        """Nonce oracle getter.

        :rtype: chainlib.nonce.NonceOracle
        :returns: Nonce oracle
        """
        return self.nonce_oracle


    def get_fee_oracle(self):
        """Fee oracle getter.

        :rtype: chainlib.fee.FeeOracle
        :returns: Fee oracle
        """
        return self.fee_oracle


    def can_sign(self):
        """Check if instance has signer capability.

        :rtype: bool
        :returns: True if signing is possible
        """
        return self.wallet != None and self.wallet.signer != None


    def get_signer(self):
        """Signer getter.

        :raises chainlib.error.SignerMissingException: Instance has no signer defined
        :rtype: Signer implementation (todo: define base interface class)
        :returns: Signer
        """
        if self.wallet.signer == None:
            raise SignerMissingException()
        return self.wallet.signer


    def get_sender_address(self):
        """Wallet address getter.

        :raises AttributeError: Instance has no signed defined
        :rtype: str
        :returns: Wallet address in canonical string representation
        """
        return self.sender_address


    def get_signer_address(self):
        if self.wallet == None:
            return None
        return self.get_sender_address()
