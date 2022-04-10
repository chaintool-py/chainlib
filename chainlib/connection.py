# standard imports
import socket
import os
import logging
import enum
import re
import json
import base64
from urllib.request import (
        Request,
        urlopen,
        urlparse,
        urljoin,
        build_opener,
        install_opener,
        )
from urllib.error import URLError

# local imports
from .jsonrpc import (
        JSONRPCRequest,
        jsonrpc_result,
        ErrorParser,
        )
from .http import PreemptiveBasicAuthHandler
from .error import (
        JSONRPCException,
        RPCException,
        )
from .auth import Auth

logg = logging.getLogger(__name__)

error_parser = ErrorParser()


class ConnType(enum.Enum):
    """Describe the underlying RPC connection type.
    """
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
    """Determine the connection type from a connection string.

    :param s: Connection string
    :type d: str
    :rtype: chainlib.connection.ConnType
    :returns: Connection type value
    """
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



class RPCConnection:
    """Base class for defining an RPC connection to a chain node.

    This class may be instantiated directly, or used as an object factory to provide a thread-safe RPC connection mechanism to a single RPC node.

    :param url: A valid URL connection string for the RPC connection
    :type url: str
    :param chain_spec: The chain spec of 
    :type chain_spec: chainlib.chain.ChainSpec
    :param auth: Authentication settings to use when connecting
    :type auth: chainlib.auth.Auth
    :todo: basic auth is currently parsed from the connection string, should be auth object instead. auth object effectively not in use.
    """

    __locations = {}
    __constructors = {
        'default': {
            },
        }
    __constructors_for_chains = {}

    def __init__(self, url=None, chain_spec=None, auth=None, verify_identity=True, timeout=1.0):
        self.timeout = timeout
        self.chain_spec = chain_spec
        self.location = None
        self.basic = None
        self.verify_identity = verify_identity
        if not self.verify_identity:
            logg.warning('RPC host identity verification is OFF. Beware, you will be easy to cheat')
        if url == None:
            return
        self.auth = auth
        if self.auth != None and not isinstance(self.auth, Auth):
            raise TypeError('auth parameter needs to be subclass of chainlib.auth.Auth')

        url_parsed = urlparse(url)
        logg.debug('creating connection {} -> {}'.format(url, url_parsed))

        # TODO: temporary basic auth parse 
        basic = url_parsed.netloc.split('@')
        location = None
        if len(basic) == 1:
            location = url_parsed.netloc
        else:
            location = basic[1]
            self.basic = basic[0].split(':')
        #if url_parsed.port != None:
        #    location += ':' + str(url_parsed.port)

        # 
        self.location = os.path.join('{}://'.format(url_parsed.scheme), location)
        self.location = urljoin(self.location, url_parsed.path)

        if url_parsed.query != '':
            self.location = urljoin(self.location, '?' + url_parsed.query)

        logg.debug('parsed url {} to location {}'.format(url, self.location))


    @staticmethod
    def from_conntype(t, tag='default'):
        """Retrieve a connection constructor from the given tag and connection type.

        :param t: Connection type
        :type t: chainlib.connection.ConnType
        :param tag: The connection selector tag
        :type tag: 
        """
        return RPCConnection.__constructors[tag][t]


    @staticmethod
    def register_constructor(conntype, c, tag='default'):
        """Associate a connection constructor for a given tag and connection type.

        The constructor must be a chainlib.connection.RPCConnection object or an object of a subclass thereof.

        :param conntype: Connection type of constructor
        :type conntype: chainlib.connection.ConnType
        :param c: Constructor
        :type c: chainlib.connection.RPCConnection
        :param tag: Tag to store the connection constructor under
        :type tag: str
        """
        if RPCConnection.__constructors.get(tag) == None:
            RPCConnection.__constructors[tag] = {}
        RPCConnection.__constructors[tag][conntype] = c
        logg.info('registered RPC connection constructor {} for type {} tag {}'.format(c, conntype, tag))


    # TODO: constructor needs to be constructor-factory, that itself can select on url type
    @staticmethod
    def register_location(location, chain_spec, tag='default', exist_ok=False):
        """Associate a URL for a given tag and chain spec.
        
        :param location: URL of RPC connection
        :type location: str
        :param chain_spec: Chain spec describing the chain behind the RPC connection
        :type chain_spec: chainlib.chain.ChainSpec
        :param tag: Tag to store the connection location under
        :type tag: str
        :param exist_ok: Overwrite existing record
        :type exist_ok: bool
        :raises ValueError: Record already exists, and exist_ok is not set
        """
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
        """Connect to the location defined by the given tag and chain spec, using the associated constructor.
    
        Location must first be registered using the RPCConnection.register_location method.

        Constructor must first be registered using the RPCConnection.register_constructor method.
        
        :param chain_spec: Chain spec part of the location record
        :type chain_spec: chainlib.chain.ChainSpec
        :param tag: Tag part of the location record
        :type tag: str
        :rtype: chainlib.connection.RPCConnection
        :returns: Instantiation of the matching registered constructor
        """
        chain_str = str(chain_spec)
        c = RPCConnection.__locations[chain_str][tag]
        constructor = RPCConnection.from_conntype(c[0], tag=tag)
        logg.debug('rpc connect {} {} {}'.format(constructor, c, tag))
        return constructor(url=c[1], chain_spec=chain_spec)


    def disconnect(self):
        """Should be overridden to clean up any resources bound by the connect method.
        """
        pass


    def __del__(self):
        self.disconnect()



class HTTPConnection(RPCConnection):
    """Generic HTTP connection subclass of RPCConnection
    """
    pass
    


class UnixConnection(RPCConnection):
    """Generic Unix socket connection subclass of RPCConnection
    """
    pass



class JSONRPCHTTPConnection(HTTPConnection):
    """Generic JSON-RPC specific HTTP connection wrapper.
    """

    def check_rpc(self):
        """Check if RPC connection is a valid JSON-RPC endpoint.

        :raises Exception: Invalid connection.
        """
        j = JSONRPCRequest()
        req = j.template()
        req['method'] = 'ping'
        try:
            self.do(req)
        except JSONRPCException:
            pass


    def check(self):
        """Check if endpoint is reachable.

        :rtype: bool
        :returns: True if reachable
        """
        try:
            self.check_rpc()    
        except URLError as e:
            logg.error('cannot connect to node {}; {}'.format(self.location, e))
            return False
        return True


    def do(self, o, error_parser=error_parser):
        """Execute a JSON-RPC query, from dict as generated by chainlib.jsonrpc.JSONRPCRequest:finalize.

        If connection was created with an auth object, the auth object will be used to authenticate the query.

        If connection was created with a basic url string, the corresponding basic auth credentials will be used to authenticate the query.

        :param o: JSON-RPC query object
        :type o: dict
        :param error_parser: Error parser object to process JSON-RPC error response with.
        :type error_parser: chainlib.jsonrpc.ErrorParser
        :raises ValueError: Invalid response from JSON-RPC endpoint
        :raises URLError: Endpoint could not be reached
        :rtype: any
        :returns: Result value part of JSON RPC response
        :todo: Invalid response exception from invalid json response
        """
        ssl_ctx = None
        if not self.verify_identity:
            import ssl
            ssl_ctx = ssl.SSLContext()
            ssl_ctx.verify_mode = ssl.CERT_NONE
        req = Request(
                self.location,
                method='POST',
                )
        req.add_header('Content-Type', 'application/json')

        # use specific auth if present
        if self.auth != None:
            p = self.auth.urllib_header()
            req.add_header(p[0], p[1])
        data = json.dumps(o)
        logg.debug('(HTTP) send {}'.format(data))

        # use basic auth if present
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
       
        r = None
        try: 
            r = urlopen(
                req,
                data=data.encode('utf-8'),
                context=ssl_ctx,
                timeout=self.timeout,
                )
        except URLError as e:
            raise RPCException(e)

        resp = r.read()
        logg.debug('(HTTP) recv {}'.format(resp.decode('utf-8')))
        result = json.loads(resp)
        if o['id'] != result['id']:
            raise ValueError('RPC id mismatch; sent {} received {}'.format(o['id'], result['id']))
        return jsonrpc_result(result, error_parser)


class JSONRPCUnixConnection(UnixConnection):
    """Execute a JSON-RPC query, from dict as generated by chainlib.jsonrpc.JSONRPCRequest:finalize.

    :param o: JSON-RPC query object
    :type o: dict
    :param error_parser: Error parser object to process JSON-RPC error response with.
    :type error_parser: chainlib.jsonrpc.ErrorParser
    :raises ValueError: Invalid response from JSON-RPC endpoint
    :raises IOError: Endpoint could not be reached
    :rtype: any
    :returns: Result value part of JSON RPC response
    :todo: Invalid response exception from invalid json response
    """

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


# TODO: Automatic creation should be hidden behind symbol, in the spirit of no unsolicited side-effects. (perhaps connection should be module dir, and jsonrpc a submodule)
RPCConnection.register_constructor(ConnType.HTTP, JSONRPCHTTPConnection, tag='default')
RPCConnection.register_constructor(ConnType.HTTP_SSL, JSONRPCHTTPConnection, tag='default')
RPCConnection.register_constructor(ConnType.UNIX, JSONRPCUnixConnection, tag='default')
