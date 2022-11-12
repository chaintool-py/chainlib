# standard imports
import os

# external imports
import confini

# local imports
#from .base import (
#        Flag,
#        argflag_std_target,
#        )
from chainlib.cli.arg import ArgFlag

script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(script_dir, '..', 'data')


def apply_groff(collection, v, arg=None, typ='arg'):
    s = ''
    for flag in collection:
        if len(s) > 0:
            s += ', '
        s += format_groff(flag, v, arg=arg, typ=typ)
    s = "\n.TP\n" + s + "\n" + v
    return s


def format_groff(k, v, arg=None, typ='arg'):
    s = ''
    if typ == 'env':
        s += '\\fI'
    else:
        s += '\\fB'
    s += k
    if arg != None:
        s += ' \\fI' + arg
    s += '\\fP'
    return s


class DocEntry:

    def __init__(self, *args, typ='arg'):
        self.flags = args
        self.render = self.get_empty
        self.groff = None
        self.typ = typ
        self.v = None


    def __check_line_default(self, m):
        if self.render == self.get_empty:
            self.render = m


    def get_empty(self):
        s = ''
        for flag in self.flags:
            if len(s) > 0:
                s += ', '
            s += flag
   
        s += '\n\t(undefined)\n'
        return s


    def set_groff(self, v):
        self.__check_line_default(self.get_groff)
        self.groff = v


    def set_groff_argvalue(self, argvalue):
        self.v = '\\fI' + argvalue + '\\fP'


    def get_groff(self):
        v = self.groff
        if v == None:
            v = self.plain
        s = apply_groff(self.flags, v, arg=self.v, typ=self.typ) 
        return s


    def __str__(self):
        return self.render()
   

class DocGenerator:

    def __init__(self, arg_flags):
        #self.config = config
        self.arg_flags = arg_flags
        self.docs = {}
        self.envs = {}
        self.__argflag_list = ArgFlag()


    def __str__(self):
        s = ''
        ks = list(self.docs.keys())
        ks.sort()
        for k in ks:
            s += str(self.docs[k]) 
            env = self.envs.get(k)
            if env != None:
                s += ' Overrides the \\fI' + env + '\\fP configuration setting.'
            s += "\n" 
        return s


    def get_args(self):
        s = ''
        ks = list(self.docs.keys())
        ks.sort()
        for k in ks:
            s += str(self.docs[k]) + "\n" 
        return s


    def set_arg(self, k, v, flags, argvalue=None):
        o = DocEntry(*flags)
        o.set_groff_argvalue(argvalue)
        o.set_groff(v)
        self.docs[k] = o


    def override_arg(self, k, v, args, argvalue=None):
        o = self.docs[k]
        #g.docs[v[0]].groff = v[1].rstrip()
        o.set_groff(v)
        if argvalue != None:
            o.set_groff_argvalue(argvalue)
        l = len(args)
        if l > 0:
            o.flags = []
        for i in range(l):
            o.flags.append(args[i])

#
#    def process_env(self):
#        for k in self.config.all():
#            if k[0] == '_':
#                continue
#            self.envs[k] = None


    def process_arg(self):

        if self.arg_flags & self.__argflag_list.VERBOSE:
            o = DocEntry('--no-logs')
            o.set_groff('Turn of logging completely. Negates \\fB-v\\fP and \\fB-vv\\fP')
            self.docs['nologs'] = o

            o = DocEntry('-v')
            o.set_groff('Verbose. Show logs for important state changes.')
            self.docs['v'] = o

            o = DocEntry('-vv')
            o.set_groff('Very verbose. Show logs with debugging information.')
            self.docs['vv'] = o

        if self.arg_flags & self.__argflag_list.CONFIG:
            o = DocEntry('-c', '--config')
            o.set_groff('Load configuration files from given directory. All files with an .ini extension will be loaded, of which all must contain valid ini file data.')
            o.set_groff_argvalue('config_dir')
            self.docs['c'] = o

            o = DocEntry('-n', '--namespace')
            o.set_groff('Load given configuration namespace. Configuration will be loaded from the immediate configuration subdirectory with the same name.')
            o.set_groff_argvalue('namespace')
            self.docs['n'] = o
           
            o = DocEntry('--dumpconfig')
            o.set_groff('Output configuration settings rendered from environment and inputs. Valid arguments are \\fIini\\fP for ini file output, and \\fIenv\\fP for environment variable output. See \\fBCONFIGURATION\\fP.')
            o.set_groff_argvalue('format')
            self.docs['dumpconfig'] = o


        if self.arg_flags & self.__argflag_list.WAIT:
            o = DocEntry('-w')
            o.set_groff('Wait for the last transaction to be confirmed on the network. Will generate an error if the EVM execution fails.')
            self.docs['w'] = o

            o = DocEntry('-ww')
            o.set_groff('Wait for \\fIall\\fP transactions sequentially to be confirmed on the network. Will generate an error if EVM execution fails for any of the transactions.')
            self.docs['ww'] = o


        if self.arg_flags & self.__argflag_list.ENV:
            o = DocEntry('--env-prefix')
            o.set_groff('Environment prefix for variables to overwrite configuration. Example: If \\fB--env-prefix\\fP is set to \\fBFOO\\fP then configuration variable \\fBBAR_BAZ\\fP would be set by environment variable \\fBFOO_BAZ_BAR\\fP. Also see \\fBENVIRONMENT\\fP.')
            self.docs['envprefix'] = o

        
        if self.arg_flags & self.__argflag_list.PROVIDER:
            o = DocEntry('-p', '--rpc-provider')
            o.set_groff('Fully-qualified URL of RPC provider.')
            self.docs['p'] = o
            self.envs['p'] = 'RPC_PROVIDER'

            o = DocEntry('--rpc-dialect')
            o.set_groff('RPC backend dialect. If specified it \\fImay\\fP help with encoding and decoding issues.')
            self.docs['rpcdialect'] = o
            self.envs['rpcdialect'] = 'RPC_DIALECT'

            if self.arg_flags & self.__argflag_list.NO_TARGET == 0:
                o = DocEntry('--height')
                o.set_groff('Block height at which to query state for. Does not apply to transactions.')
                self.docs['height'] = o

            if self.arg_flags & self.__argflag_list.RPC_AUTH:
                o = DocEntry('--rpc-auth')
                o.set_groff('RPC endpoint authentication method, e.g. how to handle a HTTP WWW-Authenticate header.')
                self.docs['rpcauth'] = o
                self.envs['rpcauth'] = 'RPC_AUTH'

                o = DocEntry('--rpc-credentials')
                o.set_groff('RPC endpoint authentication data. Format depends on the authentication method defined in \\fB--rpc-auth\\fP.')
                self.docs['rpccredentials'] = o
                self.envs['rpccredentials'] = 'RPC_CREDENTIALS'


        if self.arg_flags & self.__argflag_list.CHAIN_SPEC:
            o = DocEntry('-i', '--chain-spec')
            o.set_groff('Chain specification string, in the format <engine>:<fork>:<chain_id>:<common_name>. Example: "evm:london:1:ethereum".')
            o.set_groff_argvalue('chain_spec')
            self.docs['i'] = o
            self.envs['i'] = 'RPC_CREDENTIALS'


        if self.arg_flags & self.__argflag_list.UNSAFE:
            o = DocEntry('-u', '--unsafe')
            o.set_groff('Allow addresses that do not pass checksum.')
            self.docs['u'] = o

        
        if self.arg_flags & self.__argflag_list.SEQ:
            o = DocEntry('--seq')
            o.set_groff('Use numeric sequencial jsonrpc query ids. Useful for buggy server implementations who expects such.')
            self.docs['seq'] = o


        if self.arg_flags & self.__argflag_list.KEY_FILE:
            o = DocEntry('-y', '--key-path')
            o.set_groff('Path to signing key.')
            o.set_groff_argvalue('path')
            self.docs['y'] = o
            self.envs['y'] = 'WALLET_KEY_FILE'

            o = DocEntry('--passphrase-file')
            o.set_groff('Path to file containing password to unlock key file')
            o.set_groff_argvalue('path')
            self.docs['passphrasefile'] = o


        if self.arg_flags & self.__argflag_list.SEND:
            o = DocEntry('-s')
            o.set_groff('Send to network. If set, network state may change. This means tokens may be spent and so on. Use with care. Only applies to transactions.')
            self.docs['s'] = o


        if self.arg_flags & self.__argflag_list.RAW:
            o = DocEntry('--raw')
            o.set_groff('Produce output most optimized for machines.')
            self.docs['raw'] = o

            o = DocEntry('-0')
            o.set_groff('Omit newline to output')
            self.docs['0'] = o

        if self.arg_flags & self.__argflag_list.VALUE:
            o = DocEntry('--total')
            o.set_groff('Deduct calculated fee from value.')
            self.docs['total'] = o


        if self.arg_flags & self.__argflag_list.TAB:
            o = DocEntry('-o', '--output-key')
            o.set_groff('Include output by key name')
            self.docs['o'] = o


        if self.arg_flags & (self.__argflag_list.SIGN | self.__argflag_list.NONCE):
            o = DocEntry('--nonce')
            o.set_groff('Explicitly set nonce to use for transaction.')
            self.docs['nonce'] = o


        if self.arg_flags & (self.__argflag_list.SIGN | self.__argflag_list.FEE):
            o = DocEntry('--fee-price')
            o.set_groff('Set fee unit price to offer for the transaction. If used with \\fB-s\\fP this may incur actual network token cost.')
            self.docs['feeprice'] = o

            o = DocEntry('--fee-limit')
            o.set_groff('Set the limit of execution units for the transaction. If used with \\fB-s\\fP this may incur actual network token cost. If \\fB--fee-price\\fP is not explicitly set, the price \\fImay\\fP be retrieved from the network, and multiplied with this value to define the cost.')
            self.docs['feelimit'] = o


#        # TODO: this manipulation should be DRYd
#        if self.arg_flags & argflag_std_target == 0:
#            self.arg_flags |= self.__argflag_list.WALLET


        if self.arg_flags & self.__argflag_list.EXEC:
            o = DocEntry('-e', '--executable-address')
            o.set_groff('Address of an executable code point on the network.')
            self.docs['e'] = o

        
        if self.arg_flags & self.__argflag_list.WALLET:
            o = DocEntry('-a', '--recipient-address')
            o.set_groff('Network wallet address to operate on. For read calls, this will be the wallet address for which the query is anchored. For transaction calls, it will be the wallet address for which state will be changed.')
            self.docs['a'] = o
        
        print("docs {}".format(self.docs.keys()))

    def process(self):
        self.process_arg()
#        self.process_env()


class EnvDocGenerator:

    def __init__(self, arg_flags, override=None):
        self.arg_flags = arg_flags
        self.envs = {}
        self.__argflag_list = ArgFlag()
        env_dir = os.path.join(data_dir, 'env')
        self.config = confini.Config(env_dir, override_dirs=override)
        self.config.process()


    def __add(self, k):
        #v = format_groff(k, self.config.get(k), None, typ='env')
        v = apply_groff([k], self.config.get(k), None, typ='env')
        self.envs[k] = v


    def process(self):
        ks = []
        if self.arg_flags & self.__argflag_list.PROVIDER:
            ks += [
                    'RPC_PROVIDER',
                    'RPC_DIALECT',
                    ]
            if self.arg_flags & self.__argflag_list.RPC_AUTH:
                ks += [
                        'RPC_AUTH',
                        'RPC_CREDENTIALS',
                        ]

        if self.arg_flags & self.__argflag_list.CHAIN_SPEC:
            ks.append('CHAIN_SPEC')

        if self.arg_flags & self.__argflag_list.KEY_FILE:
            ks += [
                'WALLET_KEY_FILE',
                'WALLET_PASSPHRASE',
                    ]

        for k in ks:
            self.__add(k)


    def __len__(self):
        return len(self.envs)


    def __str__(self):
        s = ''
        ks = list(self.envs.keys())
        ks.sort()
        for k in ks:
            s += str(self.envs[k]) + "\n"  
        return s
