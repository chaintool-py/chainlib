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
from chainlib.eth.gas import (
        RPCGasOracle,
        OverrideGasOracle,
        )
from chainlib.error import SignerMissingException

logg = logging.getLogger(__name__)


class Rpc:
    
    def __init__(self, cls, wallet=None):
        self.constructor = cls
        self.id_generator = None
        self.conn = None
        self.chain_spec = None
        self.wallet = wallet
        self.nonce_oracle = None
        self.gas_oracle = None


    def connect_by_config(self, config):
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
                self.gas_oracle = OverrideGasOracle(price=fee_price, limit=fee_limit, conn=self.conn, id_generator=self.id_generator)
            else:
                self.gas_oracle = RPCGasOracle(self.conn, id_generator=self.id_generator)

        return self.conn


    def get_nonce_oracle(self):
        return self.nonce_oracle


    def get_gas_oracle(self):
        return self.gas_oracle


    def can_sign(self):
        return self.wallet != None and self.wallet.signer != None


    def get_signer(self):
        if self.wallet.signer == None:
            raise SignerMissingException()
        return self.wallet.signer


    def get_sender_address(self):
        return self.wallet.signer_address
