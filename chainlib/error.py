# TODO: use json-rpc module
class RPCException(Exception):
    """Base RPC connection error
    """
    pass


class JSONRPCException(RPCException):
    """Base JSON-RPC error
    """
    pass


class ExecutionError(Exception):
    """Base error for transaction execution failures
    """
    pass


class SignerMissingException(Exception):
    """Raised when attempting to retrieve a signer when none has been added
    """
