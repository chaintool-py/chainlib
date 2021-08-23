# standard imports
import logging

# external imports
from chainlib.chain import ChainSpec
from chainlib.connection import RPCConnection
from chainlib.jsonrpc import IntSequenceGenerator
from chainlib.eth.nonce import (
        RPCNonceOracle,
        OverrideNonceOracle,
        )
from chainlib.eth.fee import (
        RPCGasOracle,
        OverrideGasOracle,
        )
from chainlib.error import SignerMissingException

logg = logging.getLogger(__name__)


class Rpc:
    """Convenience wrapper to build rpc connection from processed configuration values.

    :param cls: RPC connection class to instantiate
    :type cls: chainlib.connection.RPCConnection implementation
    :param wallet: Add wallet backend to instance
    :type wallet: chainlib.cli.wallet.Wallet
    """
    
    def __init__(self, cls, wallet=None):
        self.constructor = cls
        self.id_generator = None
        self.conn = None
        self.chain_spec = None
        self.wallet = wallet
        self.nonce_oracle = None
        self.fee_oracle = None


    def connect_by_config(self, config):
        """Create a connection using the provided configuration, as rendered by chainlib.cli.config.Config.

        The connection url string is fetched from the "RPC_HTTP_PROVIDER" configuration key. Currently only HTTP connection is supported. Basic HTTP auth is supported using the "RPC_HTTP_USERNAME" and "RPC_HTTP_PASSWORD" keys together with "RPC_HTTP_AUTHENTICATION" set to "basic".

        The "CHAIN_SPEC" value is used for the chain context of the connection.

        If the sequence flag was set in the confiruation (which generates the configuration key "_SEQ"), a sequential integer generator will be used for rpc ids. Otherwise uuids will be used.

        If the standard arguments for nonce and fee price/price have been defined (which generate the configuration keys "_NONCE", "_FEE_PRICE" and "_FEE_LIMIT" respectively) , the corresponding overrides for fee and nonce generators will be defined.

        :param config: Processed configuration 
        :type config: confini.Config
        :rtype: chainlib.connection.RPCConnection
        :returns: An established rpc connection
        """
        auth = None
        if config.get('RPC_HTTP_AUTHENTICATION') == 'basic':
            from chainlib.auth import BasicAuth
            auth = BasicAuth(config.get('RPC_HTTP_USERNAME'), config.get('RPC_HTTP_PASSWORD'))
            logg.debug('using basic http auth')
        
        if config.get('_SEQ'):
            self.id_generator = IntSequenceGenerator()

        self.chain_spec = config.get('CHAIN_SPEC')
        self.conn = self.constructor(url=config.get('RPC_HTTP_PROVIDER'), chain_spec=self.chain_spec, auth=auth)

        if self.can_sign():
            nonce = config.get('_NONCE')
            if nonce != None:
                self.nonce_oracle = OverrideNonceOracle(self.get_sender_address(), nonce, id_generator=self.id_generator)
            else:
                self.nonce_oracle = RPCNonceOracle(self.get_sender_address(), self.conn, id_generator=self.id_generator)

            fee_price = config.get('_FEE_PRICE')
            fee_limit = config.get('_FEE_LIMIT')
            if fee_price != None or fee_limit != None:
                self.fee_oracle = OverrideGasOracle(price=fee_price, limit=fee_limit, conn=self.conn, id_generator=self.id_generator)
            else:
                self.fee_oracle = RPCGasOracle(self.conn, id_generator=self.id_generator)

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
        return self.wallet.signer_address
