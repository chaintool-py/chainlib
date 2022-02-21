# local imports
from .base import (
        Flag,
        argflag_std_target,
        )


class DocEntry:

    def __init__(self, *args, argvalue=None):
        self.flags = args
        self.v = argvalue
        self.render = self.get_empty
        self.groff = None


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


    def get_groff(self):
        s = ''
        for flag in self.flags:
            if len(s) > 0:
                s += ', '
            s += '\\fB' + flag
            if self.v != None:
                s += ' \\fI' + self.v
            s += '\\fP'

        v = self.groff
        if v == None:
            v = self.plain

        s = "\n.TP\n" + s + "\n" + self.groff
        return s


    def __str__(self):
        return self.render()
   

class DocGenerator:

    def __init__(self, arg_flags):
        self.arg_flags = arg_flags
        self.docs = {}


    def __str__(self):
        s = ''
        ks = list(self.docs.keys())
        ks.sort()
        for k in ks:
            s += str(self.docs[k]) + "\n" 
        return s


    def process(self):
        if self.arg_flags & Flag.VERBOSE:
            o = DocEntry('--no-logs')
            o.set_groff('Turn of logging completely. Negates \\fB-v\\fP and \\fB-vv\\fP')
            self.docs['nologs'] = o

            o = DocEntry('-v')
            o.set_groff('Verbose. Show logs for important state changes.')
            self.docs['v'] = o

            o = DocEntry('-vv')
            o.set_groff('Very verbose. Show logs with debugging information.')
            self.docs['vv'] = o


        if self.arg_flags & Flag.CONFIG:
            o = DocEntry('-c', '--config', argvalue='config_dir')
            o.set_groff('Load configuration files from given directory. All files with an .ini extension will be loaded, of which all must contain valid ini file data.')
            self.docs['c'] = o

            o = DocEntry('-n', '--namespace', argvalue='namespace')
            o.set_groff('Load given configuration namespace. Configuration will be loaded from the immediate configuration subdirectory with the same name.')
            self.docs['n'] = o
           
            o = DocEntry('--dumpconfig', argvalue='format')
            o.set_groff('Load given configuration namespace. Configuration will be loaded from the immediate configuration subdirectory with the same name.')
            self.docs['dumpconfig'] = o


        if self.arg_flags & Flag.WAIT:
            o = DocEntry('-w')
            o.set_groff('Wait for the last transaction to be confirmed on the network. Will generate an error if the EVM execution fails.')
            self.docs['w'] = o

            o = DocEntry('-ww')
            o.set_groff('Wait for \\fIall\\fP transactions sequentially to be confirmed on the network. Will generate an error if EVM execution fails for any of the transactions.')
            self.docs['ww'] = o


        if self.arg_flags & Flag.ENV_PREFIX:
            o = DocEntry('--env-prefix')
            o.set_groff('Environment prefix for variables to overwrite configuration. Example: If \\fB--env-prefix\\fP is set to \\fBFOO\\fP then configuration variable \\fBBAR_BAZ\\fP would be set by environment variable \\fBFOO_BAZ_BAR\\fP. Also see \\fBENVIRONMENT\\fP.')
            self.docs['envprefix'] = o

        
        if self.arg_flags & Flag.PROVIDER:
            o = DocEntry('-p', '--rpc-provider')
            o.set_groff('Fully-qualified URL of RPC provider.')
            self.docs['p'] = o

            o = DocEntry('--rpc-dialect')
            o.set_groff('RPC backend dialect. If specified it \\fImay\\fP help with encoding and decoding issues.')
            self.docs['rpcdialect'] = o

            o = DocEntry('--height')
            o.set_groff('Block height at which to query state for. Does not apply to transactions.')
            self.docs['height'] = o

            if self.arg_flags & Flag.RPC_AUTH:
                o = DocEntry('--rpc-auth')
                o.set_groff('RPC endpoint authentication method, e.g. how to handle a HTTP WWW-Authenticate header.')
                self.docs['rpcauth'] = o

                o = DocEntry('--rpc-credentials')
                o.set_groff('RPC endpoint authentication data. Format depends on the authentication method defined in \\fB--rpc-auth\\fP.')
                self.docs['rpcendpoint'] = o


        if self.arg_flags & Flag.CHAIN_SPEC:
            o = DocEntry('-i', '--chain-spec', argvalue='chain_spec')
            o.set_groff('Chain specification string, in the format <engine>:<fork>:<chain_id>:<common_name>. Example: "evm:london:1:ethereum".')
            self.docs['i'] = o


        if self.arg_flags & Flag.UNSAFE:
            o = DocEntry('-u', '--unsafe')
            o.set_groff('Allow addresses that do not pass checksum.')
            self.docs['u'] = o

        
        if self.arg_flags & Flag.SEQ:
            o = DocEntry('--seq')
            o.set_groff('Use numeric sequencial jsonrpc query ids. Useful for buggy server implementations who expects such.')
            self.docs['seq'] = o


        if self.arg_flags & Flag.KEY_FILE:
            o = DocEntry('-y', '--key-path', argvalue='path')
            o.set_groff('Path to signing key.')
            self.docs['y'] = o

            o = DocEntry('--passphrase-file', argvalue='path')
            o.set_groff('Path to file containing password to unlock key file')
            self.docs['passphrasefile'] = o


        if self.arg_flags & Flag.SEND:
            o = DocEntry('-s')
            o.set_groff('Send to network. If set, network state may change. This means tokens may be spent and so on. Use with care. Only applies to transactions.')
            self.docs['s'] = o


        if self.arg_flags & Flag.RAW:
            o = DocEntry('--raw')
            o.set_groff('Produce output most optimized for machines.')
            self.docs['raw'] = o


        if self.arg_flags & (Flag.SIGN | Flag.NONCE):
            o = DocEntry('--nonce')
            o.set_groff('Explicitly set nonce to use for transaction.')
            self.docs['nonce'] = o


        if self.arg_flags & (Flag.SIGN | Flag.FEE):
            o = DocEntry('--fee-price')
            o.set_groff('Set fee unit price to offer for the transaction. If used with \\fB-s\\fP this may incur actual network token cost.')
            self.docs['feeprice'] = o

            o = DocEntry('--fee-limit')
            o.set_groff('Set the limit of execution units for the transaction. If used with \\fB-s\fP this may incur actual network token cost. If \\fB--fee-price\\fP is not explicitly set, the price \\fImay\\fP be retrieved from the network, and multiplied with this value to define the cost.')
            self.docs['feelimit'] = o

        # TODO: this manipulation should be DRYd
        if self.arg_flags & argflag_std_target == 0:
            self.arg_flags |= Flag.WALLET


        if self.arg_flags & Flag.EXEC:
            o = DocEntry('-e', '--executable-address')
            o.set_groff('Address of an executable code point on the network.')
            self.docs['e'] = o

        
        if self.arg_flags & Flag.WALLET:
            o = DocEntry('-a', '--recipient-address')
            o.set_groff('Network wallet address to operate on. For read calls, this will be the wallet address for which the query is anchored. For transaction calls, it will be the wallet address for which state will be changed.')
            self.docs['a'] = o