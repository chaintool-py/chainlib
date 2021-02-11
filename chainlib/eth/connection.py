# standard imports
import logging
import json
import datetime
import time
from urllib.request import (
        Request,
        urlopen,
        )

# third-party imports
from hexathon import (
        add_0x,
        strip_0x,
        )

# local imports
from .error import (
        DefaultErrorParser,
        RevertEthException,
        )
from .rpc import (
        jsonrpc_template,
        jsonrpc_result,
        )

error_parser = DefaultErrorParser()
logg = logging.getLogger(__name__)


class HTTPConnection:

    def __init__(self, url):
        self.url = url


    def do(self, o, error_parser=error_parser):
        req = Request(
                self.url,
                method='POST',
                )
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(o)
        logg.debug('(HTTP) send {}'.format(data))
        res = urlopen(req, data=data.encode('utf-8'))
        o = json.load(res)
        return jsonrpc_result(o, error_parser)

    
    def wait(self, tx_hash_hex, delay=0.5, timeout=0.0):
        t = datetime.datetime.utcnow()
        i = 0
        while True:
            o = jsonrpc_template()
            o['method'] ='eth_getTransactionReceipt'
            o['params'].append(add_0x(tx_hash_hex))
            req = Request(
                    self.url,
                    method='POST',
                    )
            req.add_header('Content-Type', 'application/json')
            data = json.dumps(o)
            logg.debug('(HTTP) receipt attempt {} {}'.format(i, data))
            res = urlopen(req, data=data.encode('utf-8'))
            r = json.load(res)

            e = jsonrpc_result(r, error_parser)
            if e != None:
                logg.debug('e {}'.format(strip_0x(e['status'])))
                if strip_0x(e['status']) == '00':
                    raise RevertEthException(tx_hash_hex)
                return e

            if timeout > 0.0:
                delta = (datetime.datetime.utcnow() - t) + datetime.timedelta(seconds=delay)
                if  delta.total_seconds() >= timeout:
                    raise TimeoutError(tx_hash)

            time.sleep(delay)
            i += 1
