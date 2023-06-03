# chainlib

# Overview

Chainlib is an attempt at employing a universal interface to manipulate
and access blockchains regardless of underlying architecture.

It makes the following assumptions:

- A block MUST have a interpretable serializable format, and contains
  zero of more transactions

- A transaction MUST have a interpretable serializable format

- A transaction MUST have a nonce associated with a sender address. This
  uniquely identifies the transaction on the network.

- A transaction MUST have a fee bid to get the transaction executed on
  the network (a network that does not care about bids can just ignore
  this property).

- A transaction signature MAY be locked to a particular chain identifier

- The sender key of a transaction MAY be recovered by the signature of
  the transaction

Chainlib is specifically designed for building command line interface
tools. It provides templates for handling configuration, argument
parsing and environment variable processing to build RPC connections to
chain nodes for network queries and signing operations.

# Command line interface provisions

The base CLI provisions of `chainlib` simplifies the generation of a
some base object instances by command line arguments, environment
variables and configuration schemas.

To use CLI provisions, `chainlib.cli` should be imported. This
automatically imports the following submodules:

`arg`  
Define and/or select command-line arguments

`config`  
Process configuration from command-line arguments and environment
variables

`rpc`  
Create RPC connection from configuration

`wallet`  
Create wallet from configuration

Any chain implementation building on `chainlib` should extend one or
more of the classes in these modules as needed, for example order to add
more configuration directives or command line argument flags.

## Arguments

`chainlib` defines a set of arguments that are common concepts for
interfacing with blockchain RPCs. Which arguments to use for a specific
instantiation can be defined using flags or symbols that define groups
of flags.

This functionality is provided by the `chainlib.cli.args.ArgumentParser`
class. It is a thin wrapper around the standard library
`argparser.ArgumentParser` class, only adding a method to add arguments
to the instance based on the aforementioned flags.

Following is a description of all pre-defined arguments that are
available with `chainlib`.

### -c, –config

Override configuration directives by reading ini-files in the given
directory.

Only configuration directives defined in the schema may be overridden.
See [chainlib-config](#chainlib_002dconfig).

### –env-prefix

Prepend the given string to configuration directives when overriding by
environment variables

Normally, if a configuration directive `FOO_BAR` exists, the environment
variable `FOO_BAR` will override its value. If `--env-prefix BAZ` is
passed, the environment variable `BAZ_FOO_BAR` will be used instead to
override the configuration directive `FOO_BAR`. The environment variable
`FOO_BAR` will in this case *not* be used.

### –height

Query the chain RPC for results at a specific block height.

Applies to *read* operations only.

### -i, –chain-spec

Chain specification string for the blockchain connection.

This informs the implementing code about the architecture and deployment
of the blockchain network. It can also be relevant when creating
signatures for the network (e.g. the EIP155 signature scheme for EVM).

### –fee-limit

Use the exact given fee multiplier to calculate the final bid to get
transaction executed on the network.

How the fee semantics are employed depend on the chain implementation,
but the final resulting bid *must always* be the product of
`price * limit`.

If *not* defined, the multiplier will be retrieved using the fees
provider defined by the implementation.

### –fee-price

Use the exact given fee price as factor to calculate bid to get
transaction executed on the network.

How the fee semantics are employed depend on the chain implementation,
but the final resulting bid *must always* be the product of
`price * limit`.

If *not* defined, the current recommended price will be retrieved from
the fees provider defined by the implementation.

### -n, –namespace

Append the given namespace to implicit configuration override paths.

For example, if linux xdg-basedir path is used, a namespace argument of
`foo` in implementation domain `bar` will result in the configuration
override path `$HOME/.config/bar/foo`.

### –nonce

Start at the exact given nonce for the query.

If *not* defined, the next nonce will be retrieved from the nonce
provider defined by the implementation.

### -p, –provider

URL of the chain RPC provider.

### -s, –send

CLI tools building on chainlib should *never* submit to the network by
default. Instead, resulting transactions ready for network submission
should be output to terminal.

If the implementation wishes to allow the user to directly send to the
network, the `-s` flag *must* be used for this purpose.

### –seq

By default, a random RPC id will be generated for every RPC call.

However, some RPCs will only allow sequential serial numbers to be used
as RPC ids, in which case this flag should be used.

### –raw

Generate output suitable for passing to another command (e.g. UNIX
pipes).

### –rpc-auth

Tells the implementer which RPC authentication scheme to use (e.g.
"basic" for http basic).

### –rpc-credentials

Tells the implemented wich RPC authentication credentials to use for
selected rpc authentication scheme (e.g. "foo:bar" for user foo pass bar
in scheme "basic" a.k.a. http basic).

Credentials may for example also be a single value, like a private key,
depending on the scheme and implementation.

### –rpc-dialect

Tells the implementer to optimize query, result and error reporting for
the specific chain RPC backend dialect.

### -u, –unsafe

Allow arguments with blockchain addresses that are not checksum
protected.

### -v, -vv

Defines logging verbosity.

Specifically, `-v` will set loglevel to `INFO`, wheres `-vv` will set
loglevel to `DEBUG`.

Default loglevel is up to the implementer, but it is advisable to keep
it at `WARNING`.

### -w, -ww

Toggles blocking in relation to chain RPC calls.

If `-w` is set, the implementer should only block to obtain the result
of the *last, and as few as possible preceding* RPC transactions.

If `-ww` is set, the implementer should block to retrieve the results of
*all* of the preceding RPC transactions.

If the implementation consists of a single transaction, the effect of
`-w` and `-ww` will always be the same. Nonetheless, the implementation
will be forced to provide both arguments.

If neither flag is set, the typical consequence is that the network
transaction hash of the last transaction will be returned.

### -y, –key-file

Read private key from the given key file.

# Rendering configurations

Configurations in `chainlib` are processed, rendered and interfaced
using the `confini` python package.

In short, `confini` extends the functionality of Python’s standard
library `configparser` package to allow merging of directives by parsing
multiple ini-files from multiple directories.

Furthermore, it employs this same multi-file approach when defining a
configuration *schema*, aswell as defining source to *override* the
values defined in the schema.

See <https://gitlab.com/nolash/python-confini> for further details on
`confini`.

## Configuration schema in chainlib

The chainlib configuration schema is, along with the provided command
line arguments and environment variables, designed to cover the settings
necessary for most normal chain RPC operations.

### Configuration mapping

Below follows a mapping of configuration directives to command line
arguments and environment variables.

Note that any configuration directives prefixed by `"_"` are not defined
in the configuration schema, and are not overrideable by environment
variables. These are values typically are only valid within the context
of a single execution of the implemented tool.

| arg                     | config                | env                   |
|-------------------------|-----------------------|-----------------------|
| —                       | —                     | CONFINI_DIR [^1]      |
| -c. –config [^2]        | —                     | —                     |
| -i, –chain-spec         | CHAIN_SPEC            | CHAIN_SPEC            |
| –height                 | \_HEIGHT              | —                     |
| –fee-limit              | \_FEE_LIMIT           | —                     |
| –fee-price              | \_FEE_PRICE           | —                     |
| -n, –namespace          | CONFIG_USER_NAMESPACE | CONFIG_USER_NAMESPACE |
| –nonce                  | \_NONCE               | —                     |
| -p, –rpc-provider       | RPC_HTTP_PROVIDER     | RPC_HTTP_PROVIDER     |
| -a, -recipient          | \_RECIPIENT           | —                     |
| -e, –executable-address | \_EXEC_ADDRESS        | —                     |
| –rpc-auth               | RPC_AUTH              | RPC_AUTH              |
| —                       | RPC_PROVIDER          | RPC_PROVIDER [^3]     |
| —                       | RPC_SCHEME            | RPC_SCHEME [^4]       |
| –rpc-credentials        | RPC_CREDENTIALS       | RPC_CREDENTIALS       |
| –rpc-dialect            | RPC_DIALECT           | RPC_DIALECT           |
| -s, –send               | \_RPC_SEND            | —                     |
| –seq                    | \_SEQ                 | —                     |
| -u, –unsafe             | \_UNSAFE              | —                     |
| -w                      | \_WAIT                | —                     |
| -ww                     | \_WAIT_ALL            | —                     |
| -y, –key-file           | WALLET_KEY_FILE       | WALLET_KEY_FILE       |
| — [^5]                  | WALLET_PASSPHRASE     | WALLET_PASSPHRASE     |

Currently `chainlib` only supports HTTP(S) when building RPC connections
from command line arguments and configuration.

# Base library contents

## Pluggable method interface

The base chainlib blockchain interface is defined by the
`chainlib.interface.ChainInterface class`. All of the methods in this
class are unimplemented. Together they make up the methods necessary to
interface with *any* blockchain RPC.

It is up to the implemenenter to choose which of the methods that are
needed in any particular context. The implementer would then connect the
method symbols with actual code.

Most methods in this class will return objects that can be passed to an
RPC connection that fits the block context.

The available methods are:

`block_latest`  
Retrieve the latest block from the network

`block_by_hash`  
Retrieve the block corresponding to the given block hash

`block_by_number`  
Retrieve the block corresponding to the given block number

`block_from_src`  
Render a chainlib.block.Block derivative object from an
architecture-dependent block representation source

`block_to_src`  
Render an architecture dependent transaction representation from the
given Block object

`tx_by_hash`  
Retrieve the transaction corresponding to the given transaction hash

`tx_by_block`  
Retrieve the transaction corresponding to the given block hash and
transaction index

`tx_receipt`  
Retrieve the details of a confirmed transaction

`tx_raw`  
Generate an RPC query from raw transaction wire data

`tx_pack`  
Generate raw transaction wire data from an architecture dependent
transaction representation

`tx_unpack`  
Generate architecture dependent transaction representation from raw
transaction wire data

`tx_from_src`  
Render a chainlib.tx.Tx derivative object from an architecture-dependent
tx representation source

`tx_to_src`  
Render an architecture dependent transaction representation from the
given Tx object

`address_safe`  
Generate a checksum-safe network address

`address_normal`  
Generate an unambiguous network address

`src_normalize`  
Generate an unambiguous dictionary from the given dictionary. For
example, this can mean generating camel-case key equivalents for
snake-case values.

## The RPC interface

`chainlib.connection` currently has support for HTTP(S) and UNIX socket
RPC connections. Both rely on the Python *standard library* only
(`urllib` and `socket`).

It provides a thread-safe connection factory mechanism where connection
constructor and location pairs are associated with string labels.

There is also explicit builtin support for the JSONRPC RPC protocol,
which allows for a pluggable error translater that can be customized to
every RPC "dialect" that needs to be supported (examples are "geth" and
"openethereum" dialects of the Ethereum node fauna). Classes to handle
JSONRPC results, requests and errors are defined in the
`chainlib.jsonrpc` module.

## Blocks and transactions

Common block and transaction concepts are represented by the
`chainlib.block.Block` and `chainlib.tx.Tx` objects. These are very
minimal base-classes that need to be extended for every blockchain
implementation that is to be supported.

When building transactions, implementations of the
`chainlib.sign.Signer`, `chainlib.nonce.NonceOracle` and
`chainlib.fee.FeeOracle` interfaces will provide the transaction factory
object of the implementation with signatures, transaction nonces and
transaction fee details respectively.

## Other code features

This section lists features that are considered outside the core of the
`chainlib` package

### RPC authenticator

If you are relying on an RPC provider instead of running your own node
(although, you know you *should* run your own node, right?), then RPC
authentication may be relevant.

`chainlib.auth` provides two authentication mechanisms for HTTP:

`BasicAuth`  
The HTTP basic Authorization scheme

`CustomHeaderTokenAuth`  
Define an arbitrary header name and value

### Fee price aggregator

The `chainlib.stat.ChainStat` class provides a simple implementation of
a running average aggregator for network fee prices. This can be used to
generate more precise fee price heuristics that in turn can be fed to a
Fee Oracle.

[^1]: The `CONFINI_DIR` environment variable defines an explicit
    configuration *schema* path.

[^2]: The `-c` flag defines an explicit configuration *override* path.

[^3]: RPC_PROVIDER will always be set to the same value as
    RPC_HTTP_PROVIDER by default.

[^4]: The RPC_SCHEME configuration directive is always set to ’http’ by
    default.

[^5]: This flag is not provided because it is simply not safe to define
    passphrases as an argument on the command line.
