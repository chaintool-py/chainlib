# TODO: use json-rpc module
class RPCException(Exception):
    """Base RPC connection error
    """
    pass


class JSONRPCException(RPCException):
    """Base JSON-RPC error
    """
    pass


class InitializationError(Exception):
    """Base error for errors occurring while processing settings
    """
    pass

class ExecutionError(Exception):
    """Base error for transaction execution failures
    """
    pass


class SignerMissingException(InitializationError):
    """Raised when attempting to retrieve a signer when none has been added
    """


class RPCNonceException(RPCException):
    """RPC error for invalid nonce in transaction
    """


class DefaultErrorParser:
    """Base class for parsing RPC error repsonses
    """

    def translate(self, error):
        """Interface method called by unspeficied rpc when encountering an error

        This class method should be overriden to provide more fine-grained context for both general and implementation specific errors.

        :param error: RPC error response object
        :type error: dict
        :rtype: chainlib.error.JSONRPCException
        :returns: Descriptiv JSONRPCException 
        """
        return RPCException('default parser code {}'.format(error))
