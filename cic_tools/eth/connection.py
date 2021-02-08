import logging
import json
from urllib.request import (
        Request,
        urlopen,
        )

from .error import DefaultErrorParser
from .method import jsonrpc_result

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
