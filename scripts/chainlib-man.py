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
from chainlib.cli.base import (
        argflag_std_base,
        flag_names,
        )
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

argparser = argparse.ArgumentParser()
argparser.add_argument('-b', default=add_0x(hex(argflag_std_base)), help='argument flag bitmask')
argparser.add_argument('-c', help='config override directory')
argparser.add_argument('-n', help='tool name to use for man filename')
argparser.add_argument('-d', default='.', help='output directory')
argparser.add_argument('-v', action='store_true', help='turn on debug logging')
argparser.add_argument('--overrides-file', dest='overrides_file', help='load options description override from file')
argparser.add_argument('--overrides-env-dir', dest='overrides_env_dir', help='load envionment description override config from directory')
argparser.add_argument('--overrides-config-file', dest='overrides_config_file', help='load configuration text from file')
argparser.add_argument('header_file', help='groff file containing heading, synopsis and description')
args = argparser.parse_args(sys.argv[1:])

if args.v:
    logg.setLevel(logging.DEBUG)
            
b = bytes.fromhex(strip_0x(args.b))
flags = int.from_bytes(b, byteorder='big')

flags_debug= flag_names(flags)
logg.debug('apply arg flags {}: {}'.format(flags, ', '.join(flags_debug)))

g = DocGenerator(flags)

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


ge = EnvDocGenerator(flags, override=args.overrides_env_dir)
ge.process()

f = open(args.header_file)
head = f.read()
f.close()

if args.overrides_config_file != None:
    f = open(args.overrides_config_file, 'r')
    configuration_description = f.read()
    f.close()

(fd, fp) = tempfile.mkstemp()
f = os.fdopen(fd, 'w')
f.write(head)
f.write(str(g))
f.write(configuration_description)
f.write(".SH ENVIRONMENT\n\n")
f.write(str(ge))
f.write(legal_description)
f.write(source_description)
f.write(seealso_description)
f.close()

dest = os.path.join(args.d, toolname + '.1')
shutil.copyfile(fp, dest)

os.unlink(fp)
