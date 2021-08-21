# standard imports
import logging

logg = logging.getLogger(__name__)


class ChainInterface:
    """Common interface for all chain RPC query generators.

    This class should be overridden for every implementation of chain architecture RPC.

    It is up to the implementer which of the symbols to implement code for. Any implemented symbols should be associated using the ChainInterface.set method. 

    All implemented methods must generate RPC queries ready to submit using an implementation of chainlib.connection.RPCConnection 
    """

    interface_name = 'custom'

    def __unimplemented(*args, **kwargs):
        raise NotImplementedError()


    def __init__(self):
        self._block_latest = self.__unimplemented
        self._block_by_hash = self.__unimplemented
        self._block_by_number = self.__unimplemented
        self._block_from_src = self.__unimplemented
        self._block_to_src = self.__unimplemented
        self._tx_by_hash = self.__unimplemented
        self._tx_by_block = self.__unimplemented
        self._tx_receipt = self.__unimplemented
        self._tx_raw = self.__unimplemented
        self._tx_pack = self.__unimplemented
        self._tx_unpack = self.__unimplemented
        self._tx_from_src = self.__unimplemented
        self._tx_to_src = self.__unimplemented
        self._address_safe = self.__unimplemented
        self._address_normal = self.__unimplemented
        self._src_normalize = self.__unimplemented


    def block_latest(self, *args, **kwargs):
        """Retrieve the last block known to the node.

        :rtype: dict
        :returns: rpc query object
        """
        return self._block_latest(*args, **kwargs)


    def block_by_hash(self, hsh, *args, **kwargs):
        """Retrieve the block representation from the given block hash

        :param hsh: Block hash, as hex
        :type hsh: str
        :param id_generator: JSONRPC id generator
        :type id_generator: JSONRPCIdGenerator
        :rtype: dict
        :returns: rpc query object
        """
        return self._block_by_hash(hsh, *args, **kwargs)


    def block_by_number(self, idx, *args, **kwargs):
        """Retrieve the block representation from the given block height index

        :param idx: Block index number
        :type idx: int
        :param id_generator: JSONRPC id generator
        :type id_generator: JSONRPCIdGenerator
        :rtype: dict
        :returns: rpc query object
        """
        return self._block_by_number(idx, *args, **kwargs)


    def block_from_src(self, src):
        """Instantiate an implementation specific block object from the block representation returned from an RPC result

        :param src: Block source
        :type src: dict
        :param id_generator: JSONRPC id generator
        :type id_generator: JSONRPCIdGenerator
        :rtype: chainlib.block.Block
        :returns: Block object
        """
        return self._block_from_src(src)


    def block_to_src(self, block):
        """Implementation specific serialization of a block object

        :param block: Block object
        :type block: chainlib.block.Block
        :param id_generator: JSONRPC id generator
        :type id_generator: JSONRPCIdGenerator
        :rtype: dict
        :returns: Serialized block object
        """
        return self._block_to_src()


    def tx_by_hash(self, hsh, *args, **kwargs):
        """Retrieve the transaction representation by the given transaction hash

        :param hsh: Transaction hash, as hex
        :type hsh: str
        :param id_generator: JSONRPC id generator
        :type id_generator: JSONRPCIdGenerator
        :rtype: dict
        :returns: rpc query object
        """
        return self._tx_by_hash(hsh, *args, **kwargs)


    def tx_by_block(self, hsh, idx, *args, **kwargs):
        """Retrieve the transaction representation by the given block hash and transaction index

        :param hsh: Block hash, as hex
        :type hsh: str
        :param idx: Transaction index
        :type idx: int
        :param id_generator: JSONRPC id generator
        :type id_generator: JSONRPCIdGenerator
        :rtype: dict
        :returns: rpc query object

        """
        return self._tx_by_block(hsh, idx, *args, **kwargs)


    def tx_receipt(self, hsh, *args, **kwargs):
        """Retrieve representation of confirmed transaction result for given transaction hash

        :param hsh: Transaction hash, as hex
        :type hsh: str
        :param id_generator: JSONRPC id generator
        :type id_generator: JSONRPCIdGenerator
        :rtype: dict
        :returns: rpc query object
        """
        return self._tx_receipt(hsh, *args, **kwargs)


    def tx_raw(self, data, *args, **kwargs):
        """Create a raw transaction query from the given wire format

        :param data: Transaction wire format, in hex
        :type data: str
        :param id_generator: JSONRPC id generator
        :type id_generator: JSONRPCIdGenerator
        :rtype: dict
        :returns: rpc query object

        """
        return self._tx_raw(data, *args, **kwargs)


    def tx_pack(self, tx, chain_spec):
        """Generate wire format for transaction

        :param tx: Transaction object
        :type tx: dict
        :param chain_spec: Chain spec to generate wire format for
        :type chain_spec: chainlib.chain.ChainSpec
        :rtype: bytes
        :returns: Wire format, in bytes
        """
        return self._tx_pack(tx, chain_spec)


    def tx_unpack(self, data, chain_spec):
        """Generate transaction representation from wire format.

        :param data: Wire format, in bytes
        :type data: bytes
        :param chain_spec: Chain spec to parse wire format with
        :type chain_spec: chainlib.chain.ChainSpec
        :rtype: dict
        :returns: Transaction representation
        """
        return self._tx_unpack(data, chain_spec)


    def tx_from_src(self, src, block=None):
        """Instantiate transaction object from implementation specific transaction representation.

        :param src: Transaction representation
        :type src: dict
        :param block: Block object which transaction has been included in
        :type block: chainlib.block.Block
        :rtype: chainlib.tx.Tx
        :returns: Transaction object
        """
        return self._tx_from_src(src, block)


    def tx_to_src(self, tx):
        """Generate implementation specific transaction representation from transaction object.

        :param tx: Transaction object
        :type tx: chainlib.tx.Tx
        :rtype: dict
        :returns: Transaction representation
        """
        return self._tx_to_src(tx)


    def address_safe(self, address):
        """Generate implementation specific checksummed version of a crypto address.

        :param address: Potentially unsafe address
        :type address: str
        :rtype: str
        :returns: Checksummed address
        """
        return self._address_safe(address)


    def address_normal(self, address):
        """Generate normalized version of a crypto address.

        :param address: Crypto address
        :type address: str
        :rtype: str
        :returns: Normalized address
        """
        return self._address_normal(address)


    def src_normalize(self, src):
        """Generate a normalized source of an object representation.

        :param src: Object representation source
        :type src: dict
        :rtype: dict
        :returns: Normalized representation
        """
        return self._src_normalize(src)


    def set(self, method, target):
        """Associate object with method symbol.

        :param method: Method string
        :type method: str
        :param target: Target method
        :type target: object
        :raises AttributeError: Invalid method
        """
        imethod = '_' + method
        if not hasattr(self, imethod):
            raise AttributeError('invalid method {}'.format(imethod))
        setattr(self, imethod, target)
        logg.debug('set method {} on interface {}'.format(method, self.interface_name))
