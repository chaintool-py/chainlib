#!/usr/bin/python3

import logging
import os
import sys
import argparse
import tempfile
import shutil

from hexathon import strip_0x, add_0x

from chainlib.cli.man import (
        DocGenerator,
        apply_groff,
        )
from chainlib.cli.base import argflag_std_base
from chainlib.cli.arg import ArgumentParser as ChainlibArgumentParser
from chainlib.eth.cli.config import Config
        

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

argparser = argparse.ArgumentParser()
argparser.add_argument('-b', default=add_0x(hex(argflag_std_base)), help='argument flag bitmask')
argparser.add_argument('-c', help='config override directory')
argparser.add_argument('-n', help='tool name to use for man filename')
argparser.add_argument('-d', default='.', help='output directory')
argparser.add_argument('-v', action='store_true', help='turn on debug logging')
argparser.add_argument('--overrides-file', dest='overrides_file', help='load options description override from file')
argparser.add_argument('--overrides-env-file', dest='overrides_env_file', help='load envionment description overrides from file')
argparser.add_argument('header_file', help='groff file containing heading, synopsis and description')
args = argparser.parse_args(sys.argv[1:])

if args.v:
    logg.setLevel(logging.DEBUG)
            

b = bytes.fromhex(strip_0x(args.b))
flags = int.from_bytes(b, byteorder='little')

empty_args = ChainlibArgumentParser(flags).parse_args([])
config = Config.from_args(empty_args, arg_flags=flags)
g = DocGenerator(flags, config)

toolname = args.n
if toolname == None:
    parts = os.path.splitext(os.path.basename(args.header_file))
    toolname = parts[0]

g.process()

if args.overrides_file != None:
    f = open(args.overrides_file, 'r')
    while True:
        s = f.readline()
        if len(s) == 0:
            break
        v = s.split('\t', maxsplit=2)
        fargs = None
        try:
            fargs = v[2].rstrip().split(',')
        except IndexError:
            fargs = []
        g.override_arg(v[0], v[1], fargs)
    f.close()


s_env = ''
if args.overrides_env_file != None:
    f = open(args.overrides_env_file, 'r')
    while True:
        s = f.readline()
        if len(s) == 0:
            break
        (k, description) = s.split('\t', maxsplit=1)
        v = config.get(k)
        s_env += apply_groff([k], description)

print(s_env)

f = open(args.header_file)
head = f.read()
f.close()

(fd, fp) = tempfile.mkstemp()
f = os.fdopen(fd, 'w')
f.write(head)
f.write(str(g))
f.close()

dest = os.path.join(args.d, toolname + '.1')
shutil.copyfile(fp, dest)

os.unlink(fp)
