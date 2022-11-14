# chainlib

Chainlib is a prototype attempt at writing a generalized code library structure in python3 for concepts that are valid across blockchains, either within the same chain technology or across them. If useful and/or successful, it should be considered ported to a more performant language (rust?).

It is primarily aimed at (possibly threaded) console-environment development.

It aims to give fine-grained control and transparency to all operations and transformations. 

It library code should be easy to understand and maintain.

To achieve transparency and improve maintainability, it deliberately exposes the _user_ of this code to a certain degree of complexity.

Ultimately, the chainlib library is for the developer who seeks to understand and contribute, rather than merely defer and consume.


## Requirements

Chainlib seeks to keep its dependency graph and small as possible. Because of baggage from the initial phase of development, it depends on the `crypto-dev-signer` library to represent transaction structures. As this dependency also includes other routines not necessary for the code in the library, it will be replaced with a dedicated component. `crypto-dev-signer` will still be used as default for tests, and for the time being also for the CLI runnables.

To generate the bitcoin-style keccak256 hashes, `pysha3` is used. `pysha3` is a very fast python wrapper around the official keccak implementation from [XKCP](https://github.com/XKCP/XKCP).

The other requirements are very this code fragments that merely help to relieve a bit of tedium, and add no magic.

Chainlib is not compatible with python2, nor is there any reason to expect it will aim to be.


## Structure

Any generalizable structures and code can be found in the base module directory `chainlib/`

Currently the only operational code for available targets is for the `evm` and the `Ethereum` network protocol. This code can be found in the separate package `chainlib-eth`.

Every module will have a subdirectory `runnable` which contains CLI convenience tooling for common operations. Any directory `example` will contain code snippets demonstrating usage.


## How to use

There are no (exhaustive) tutorial planned for chainlib. All you need to know should be possible to easily understand from code in the `example` `tests` and `runnable` subfolders.


## See also

* The [chainsyncer](https://git.defalsify.org/chainsyncer) project, which provides a simple chain syncer framework allowing for an arbitrary amount of pluggable code to be executed for each block transaction.
* The [chainqueue](https://git.defalsify.org/chainqueue) project, which provides a transaction queueing daemon that handles conditional submisssion and resubmission of transactions to the network.
