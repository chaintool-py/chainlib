# standard imports
import socket
import os
import logging
import enum
import re
import json
from urllib.request import (
        Request,
        urlopen,
        urlparse,
        urljoin,
        build_opener,
        install_opener,
        )

# local imports
from .jsonrpc import (
        jsonrpc_template,
        jsonrpc_result,
        DefaultErrorParser,
        )
from .http import PreemptiveBasicAuthHandler

logg = logging.getLogger().getChild(__name__)

error_parser = DefaultErrorParser()


class ConnType(enum.Enum):

    CUSTOM = 0x00
    HTTP = 0x100
    HTTP_SSL = 0x101
    WEBSOCKET = 0x200
    WEBSOCKET_SSL = 0x201
    UNIX = 0x1000


re_http = '^http(s)?://'
re_ws = '^ws(s)?://'
re_unix = '^ipc://'

def str_to_connspec(s):
    if s == 'custom':
        return ConnType.CUSTOM

    m = re.match(re_http, s)
    if m != None:
        if m.group(1) != None:
            return ConnType.HTTP_SSL
        return ConnType.HTTP

    m = re.match(re_ws, s)
    if m != None:
        if m.group(1) != None:
            return ConnType.WEBSOCKET_SSL
        return ConnType.WEBSOCKET


    m = re.match(re_unix, s)
    if m != None:
        return ConnType.UNIX

    raise ValueError('unknown connection type {}'.format(s))


class RPCConnection():

    __locations = {}
    __constructors = {
        'default': {
            },
        }
    __constructors_for_chains = {}

    def __init__(self, url=None, chain_spec=None):
        self.chain_spec = chain_spec
        self.location = None
        self.basic = None
        if url == None:
            return

        url_parsed = urlparse(url)
        logg.debug('creating connection {} -> {}'.format(url, url_parsed))
        basic = url_parsed.netloc.split('@')
        location = None
        if len(basic) == 1:
            location = url_parsed.netloc
        else:
            location = basic[1]
            self.basic = basic[0].split(':')
        #if url_parsed.port != None:
        #    location += ':' + str(url_parsed.port)

        self.location = os.path.join('{}://'.format(url_parsed.scheme), location)
        self.location = urljoin(self.location, url_parsed.path)

        logg.debug('parsed url {} to location {}'.format(url, self.location))


    @staticmethod
    def from_conntype(t, tag='default'):
        return RPCConnection.__constructors[tag][t]


    @staticmethod
    def register_constructor(t, c, tag='default'):
        if RPCConnection.__constructors.get(tag) == None:
            RPCConnection.__constructors[tag] = {}
        RPCConnection.__constructors[tag][t] = c
        logg.info('registered RPC connection constructor {} for type {} tag {}'.format(c, t, tag))


    # TODO: constructor needs to be constructor-factory, that itself can select on url type
    @staticmethod
    def register_location(location, chain_spec, tag='default', exist_ok=False):
        chain_str = str(chain_spec)
        if RPCConnection.__locations.get(chain_str) == None:
            RPCConnection.__locations[chain_str] = {}
        elif not exist_ok:
            v = RPCConnection.__locations[chain_str].get(tag)
            if v != None:
                raise ValueError('duplicate registration of tag {}:{}, requested {} already had {}'.format(chain_str, tag, location, v))
        conntype = str_to_connspec(location)
        RPCConnection.__locations[chain_str][tag] = (conntype, location)
        logg.info('registered rpc connection {} ({}/{}) as {}'.format(location, chain_str, tag, conntype))


    @staticmethod
    def connect(chain_spec, tag='default'):
        chain_str = str(chain_spec)
        c = RPCConnection.__locations[chain_str][tag]
        constructor = RPCConnection.from_conntype(c[0], tag=tag)
        logg.debug('rpc connect {} {} {}'.format(constructor, c, tag))
        return constructor(url=c[1], chain_spec=chain_spec)


class HTTPConnection(RPCConnection):
    
    def disconnect(self):
        pass


    def __del__(self):
        self.disconnect()


class UnixConnection(RPCConnection):

    def disconnect(self):
        pass


    def __del__(self):
        self.disconnect()


class JSONRPCHTTPConnection(HTTPConnection):

    def do(self, o, error_parser=error_parser):
        req = Request(
                self.location,
                method='POST',
                )
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(o)
        logg.debug('(HTTP) send {}'.format(data))

        if self.basic != None:
            handler = PreemptiveBasicAuthHandler()
            handler.add_password(
                    realm=None,
                    uri=self.location,
                    user=self.basic[0],
                    passwd=self.basic[1],
                    )
            ho = build_opener(handler)
            install_opener(ho)
        
        r = urlopen(req, data=data.encode('utf-8'))
        result = json.load(r)
        logg.debug('(HTTP) recv {}'.format(result))
        if o['id'] != result['id']:
            raise ValueError('RPC id mismatch; sent {} received {}'.format(o['id'], result['id']))
        return jsonrpc_result(result, error_parser)


class JSONRPCUnixConnection(UnixConnection):

    def do(self, o, error_parser=error_parser):
        conn = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM, proto=0)
        conn.connect(self.location)
        data = json.dumps(o)

        logg.debug('unix socket send {}'.format(data))
        l = len(data)
        n = 0
        while n < l:
            c = conn.send(data.encode('utf-8'))
            if c == 0:
                s.close()
                raise IOError('unix socket ({}/{}) {}'.format(n, l, data))
            n += c
        r = b''
        while True:
            b = conn.recv(4096)
            if len(b) == 0:
                break
            r += b
        conn.close()
        logg.debug('unix socket recv {}'.format(r.decode('utf-8')))
        result = json.loads(r)
        if result['id'] != o['id']:
            raise ValueError('RPC id mismatch; sent {} received {}'.format(o['id'], result['id']))

        return jsonrpc_result(result, error_parser)


RPCConnection.register_constructor(ConnType.HTTP, JSONRPCHTTPConnection, tag='default')
RPCConnection.register_constructor(ConnType.HTTP_SSL, JSONRPCHTTPConnection, tag='default')
RPCConnection.register_constructor(ConnType.UNIX, JSONRPCUnixConnection, tag='default')
