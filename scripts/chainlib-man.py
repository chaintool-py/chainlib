#!/usr/bin/python3

import logging
import os
import sys
import argparse
import tempfile
import shutil

from hexathon import strip_0x, add_0x

from chainlib.cli.man import (
        EnvDocGenerator,
        DocGenerator,
        apply_groff,
        )
from chainlib.cli.arg import ArgFlag
#from chainlib.cli.base import (
#        argflag_std_base,
#        flag_names,
#        )
from chainlib.cli.arg import ArgumentParser as ChainlibArgumentParser
from chainlib.cli.config import Config
        

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()


configuration_description = """
.SH CONFIGURATION

All configuration settings may be overriden both by environment variables, or by overriding settings with the contents of ini-files in the directory defined by the \\fB-c\\fP option.

The active configuration, with values assigned from environment and arguments, can be output using the \\fB--dumpconfig\\fP \\fIformat\\fP option. Note that entries having keys prefixed with underscore (e.g. _SEQ) are not actual configuration settings, and thus cannot be overridden with environment variables.

To refer to a configuration setting by environment variables, the \\fIsection\\fP and \\fIkey\\fP are concatenated together with an underscore, and transformed to upper-case. For example, the configuration variable \\fIFOO_BAZ_BAR\\fP refers to an ini-file entry as follows:

.EX
[foo]
bar_baz = xyzzy
.EE

In the \\fBENVIRONMENT\\fP section below, the relevant configuration settings for this tool is listed along with a short description of its meaning.

Some configuration settings may also be overriden by command line options. Also note that the use of the \\fB-n\\fP and \\fB--env-prefix\\fP options affect how environment and configuration is read. The effects of options on how configuration settings are affective is described in the respective \\fBOPTIONS\\fP section.

"""

seealso_description = """
.SH SEE ALSO

.BP
confini-dump(1), eth-keyfile(1)

"""

legal_description = """
.SH LICENSE

This documentation and its source is licensed under the Creative Commons Attribution-Sharealike 4.0 International license.

The source code of the tool this documentation describes is licensed under the GNU General Public License 3.0.

.SH COPYRIGHT

Louis Holbrook <dev@holbrook.no> (https://holbrook.no)
PGP: 59A844A484AC11253D3A3E9DCDCBD24DD1D0E001

"""

source_description = """

.SH SOURCE CODE

https://git.defalsify.org

"""

argflag = ArgFlag()

argparser = argparse.ArgumentParser()
argparser.add_argument('-b', default=add_0x(hex(argflag.get('std_base'))), help='argument flag bitmask')
argparser.add_argument('-c', help='config override directory')
argparser.add_argument('-n', required=True, help='tool name to use for man filename')
argparser.add_argument('-d', default='.', help='output directory')
argparser.add_argument('-v', action='store_true', help='turn on debug logging')
#argparser.add_argument('--overrides-dir', dest='overrides_dir', help='load options description override from file')
argparser.add_argument('--overrides-env-dir', dest='overrides_env_dir', help='load envionment description override config from directory')
argparser.add_argument('--overrides-config-file', dest='overrides_config_file', help='load configuration text from file')
argparser.add_argument('source_dir', help='directory containing sources for the tool man page')
args = argparser.parse_args(sys.argv[1:])

if args.v:
    logg.setLevel(logging.DEBUG)

b = bytes.fromhex(strip_0x(args.b))
flags = int.from_bytes(b, byteorder='big')
flags_debug = argflag.names(flags)

logg.debug('apply arg flags {}: {}'.format(flags, ', '.join(flags_debug)))

# TODO: unfortunately, if arguments are added in chainlib/cli/arg.py  they still also have to be manually added in chainlib/cli/man.py
g = DocGenerator(flags)

toolname = args.n
g.process()

def apply_override(g, override_dir):
    #if args.overrides_dir != None:
    overrides_file = os.path.join(override_dir, toolname + '.overrides')
    override = True
    f = None
    try:
        f = open(overrides_file, 'r')
    except FileNotFoundError:
        logg.debug('no overrides found for {}'.format(toolname))
        override = False

    if override:
        while True:
            s = f.readline()
            if len(s) == 0:
                break
            v = s.split('\t', maxsplit=4)
            fargs = None
            try:
                fargs = v[2].rstrip().split(',')
            except IndexError:
                fargs = []
            argvalue = None
            if len(v) == 4:
                argvalue = v[3]
            try:
                g.override_arg(v[0], v[1], fargs, argvalue=argvalue)
            except KeyError:
                logg.info('adding not previously registered key {} flags: {}'.format(v[0], ','.join(fargs)))
                g.set_arg(v[0], v[1], fargs, argvalue=argvalue)
        f.close()
    return g


def get_head(tool_name, source_dir):
    header_file = os.path.join(source_dir, tool_name + '.head.groff') 
    f = open(header_file, 'r')
    head = f.read()
    f.close()
    return head


def get_examples(tool_name, source_dir):
    example_file = os.path.join(source_dir, tool_name + '.examples.groff')
    f = None
    try:
        f = open(example_file, 'r')
    except FileNotFoundError:
        logg.debug('no examples file found for {}'.format(tool_name))
        return None
    logg.info('examples file {} found for {}'.format(example_file, tool_name))
    examples = f.read()
    f.close()
    return examples


def get_custom(tool_name, source_dir):
    custom_file = os.path.join(source_dir, tool_name + '.custom.groff')
    f = None
    try:
        f = open(custom_file, 'r')
    except FileNotFoundError:
        logg.debug('no custom file found for {}'.format(tool_name))
        return None
    logg.info('custom file {} found for {}'.format(custom_file, tool_name))
    custom = f.read()
    f.close()
    return custom


def get_seealso(tool_name, source_dir):
    seealso_file = os.path.join(source_dir, tool_name + '.seealso.groff')
    f = None
    try:
        f = open(seealso_file, 'r')
    except FileNotFoundError:
        logg.debug('no seealso file found for {}'.format(tool_name))
        return None
    logg.info('seealso file {} found for {}'.format(seealso_file, tool_name))
    seealso = f.read()
    f.close()
    return seealso


g = apply_override(g, args.source_dir)

ge = EnvDocGenerator(flags, override=args.overrides_env_dir)
ge.process()

head = get_head(toolname, args.source_dir)
examples = get_examples(toolname, args.source_dir)
custom = get_custom(toolname, args.source_dir)
seealso = get_seealso(toolname, args.source_dir)

if args.overrides_config_file != None:
    f = open(args.overrides_config_file, 'r')
    configuration_description = f.read()
    f.close()

(fd, fp) = tempfile.mkstemp()
f = os.fdopen(fd, 'w')
f.write(head)
f.write(str(g))
f.write(configuration_description)

if custom != None:
    f.write(custom)

if examples != None:
    f.write(".SH EXAMPLES\n\n")
    f.write(examples)

if seealso != None:
    seealso_description = seealso

if len(ge) > 0:
    f.write(".SH ENVIRONMENT\n\n")
    f.write(str(ge))

f.write(legal_description)
f.write(source_description)
f.write(seealso_description)
f.close()

dest = os.path.join(args.d, toolname + '.1')
shutil.copyfile(fp, dest)

os.unlink(fp)
