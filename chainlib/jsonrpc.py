# standard imports
import uuid

# local imports
from .error import JSONRPCException

# TODO: Move all contents in this file to independent package


class JSONRPCIdGenerator:
    
    def next(self):
        raise NotImplementedError


class UUIDGenerator(JSONRPCIdGenerator):
    """Create uuid ids for JSON-RPC queries.
    """

    def next(self):
        """Create a new id

        :rtype: str
        :returns: uuid string
        """
        return str(uuid.uuid4())


class IntSequenceGenerator(JSONRPCIdGenerator):
    """Create sequential numeric ids for JSON-RPC queries.
    
    :param start: Start at the specificed numeric id
    :type start: int
    """
    def __init__(self, start=0):
        self.id = start


    def next(self):
        """Get the next id in the sequence.

        :rtype: int
        :returns: numeric id
        """
        next_id = self.id
        self.id += 1
        return next_id


default_id_generator = UUIDGenerator()


class ErrorParser:
    """Base class for parsing JSON-RPC error repsonses
    """

    def translate(self, error):
        """Interface method called by jsonrpc_result when encountering an error

        This class method may be overriden to provide more fine-grained context for both general and implementation specific errors.

        :param error: JSON-RPC error response object
        :type error: dict
        :rtype: chainlib.error.JSONRPCException
        :returns: Descriptiv JSONRPCException 
        """
        return JSONRPCException('default parser code {}'.format(error))


# deprecated symbol, provided for backward compatibility
DefaultErrorParser = ErrorParser


class JSONRPCRequest:
    """JSON-RPC request builder class.

    :param id_generator: Generator to use to define the id of the request.
    :type id_generator: chainlib.jsonrpc.JSONRPCIdGenerator
    """
    def __init__(self, id_generator=default_id_generator):
        if id_generator == None:
            id_generator = default_id_generator
        self.id_generator = id_generator


    def template(self):
        """Return a empty json-rpc 2.0 dictionary query object

        :rtype: dict
        :returns: json-rpc query object
        """
        return {
            'jsonrpc': '2.0',
            'id': None,
            'method': None,
            'params': [],
                }


    def finalize(self, request):
        """Apply next json-rpc id to json-rpc dictionary query object

        :param request: json-rpc query
        :type request: dict
        :rtype: dict
        :returns: json-rpc query with id added
        """
        request['id'] = self.id_generator.next()
        return request


def jsonrpc_response(request_id, result):
        """Create a json-rpc dictionary response object from the given id an result value.

        :param request_id: json-rpc query id
        :type request_id: str or int
        :param result: result value
        :type result: any json-serializable value
        :rtype: dict
        :result: json-rpc response object
        """
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': result,
            }


def jsonrpc_error(request_id, code=-32000, message='Server error'):
    """Create a json-rpc dictionary error object for the given id with error code and message.

    :param request_id: json-rpc query id
    :type request_id: str or int
    :param code: json-rpc error code
    :type code: int
    :param message: Error message
    :type message: str
    :rtype: dict
    :returns: json-rpc error object
    """
    return {
        'jsonrpc': '2.0',
        'id': request_id,
        'error': {
            'code': code,
            'message': message,
            },
        }


def jsonrpc_result(o, ep):
    """Retrieve the result from a json-rpc response object.

    If the result object is an error, the provided error parser will be used to generate the corresponding exception.

    :param o: json-rpc response object
    :type o: dict
    :param ep: Error parser
    :type ep: chainlib.jsonrpc.ErrorParser
    :raises JSONRPCException: exception encapsulating the error value of the response
    :rtype: any json-deserializable value
    :returns: The result value of the response
    """
    if o.get('error') != None:
        raise ep.translate(o)
    return o['result']
