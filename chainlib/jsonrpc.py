# standard imports
import uuid

# local imports
from .error import JSONRPCException


class DefaultErrorParser:

    def translate(self, error):
        return JSONRPCException('default parser code {}'.format(error))


def jsonrpc_template():
    return {
        'jsonrpc': '2.0',
        'id': str(uuid.uuid4()),
        'method': None,
        'params': [],
            }

def jsonrpc_result(o, ep):
    if o.get('error') != None:
        raise ep.translate(o)
    return o['result']


def jsonrpc_response(request_id, result):
    return {
        'jsonrpc': '2.0',
        'id': request_id,
        'result': result,
        }

def jsonrpc_error(request_id, code=-32000, message='Server error'):
    return {
        'jsonrpc': '2.0',
        'id': request_id,
        'error': {
            'code': code,
            'message': message,
            },
        }
