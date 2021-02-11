# standard imports
import uuid


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
