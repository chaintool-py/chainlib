# standard imports
import unittest
import os
import logging

# external imports
from aiee.arg import process_args

# local imports
#from chainlib.cli.base import argflag_std_base
from chainlib.cli.arg import (
        ArgFlag,
        Arg,
        ArgumentParser,
        )
from chainlib.cli.config import (
        Config,
        process_config,
        )
script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(script_dir, 'testdata')
config_dir = os.path.join(data_dir, 'config')

logging.basicConfig(level=logging.DEBUG)


class TestCli(unittest.TestCase):

    def setUp(self):
        self.flags = ArgFlag()
        self.arg = Arg(self.flags)


    def test_args_process_single(self):
        ap = ArgumentParser()
        flags = self.flags.VERBOSE | self.flags.CONFIG
        process_args(ap, self.arg, flags)

        argv = [
            '-vv',
            '-n',
            'foo',
                ]
        args = ap.parse_args(argv)
        config = Config(config_dir)
        config = process_config(config, self.arg, args, flags)
        self.assertEqual(config.get('CONFIG_USER_NAMESPACE'), 'foo')


    def test_args_process_schema_override(self):
        ap = ArgumentParser()
        flags = self.flags.VERBOSE | self.flags.CONFIG
        process_args(ap, self.arg, flags)

        args = ap.parse_args([])

        config = Config(config_dir)
        config = process_config(config, self.arg, args, flags)
        self.assertEqual(config.get('FOO_BAR'), 'baz')


    def test_args_process_arg_override(self):
        ap = ArgumentParser()
        flags = self.flags.VERBOSE | self.flags.CONFIG
        process_args(ap, self.arg, flags)

        argv = [
            '-c',
            config_dir,
            '-n',
            'foo',
            ]
        args = ap.parse_args(argv)
        config = Config(config_dir, namespace=args.namespace)
        config = process_config(config, self.arg, args, flags)
        self.assertEqual(config.get('FOO_BAR'), 'bazbazbaz')


    def test_args_process_internal_override(self):
        ap = ArgumentParser()
        flags = self.flags.VERBOSE | self.flags.CONFIG | self.flags.CHAIN_SPEC
        process_args(ap, self.arg, flags)

        args = ap.parse_args()
        default_config_dir = os.path.join(config_dir, 'default')

        config = Config(default_config_dir)
        config = process_config(config, self.arg, args, flags)
        self.assertEqual(config.get('CHAIN_SPEC'), 'baz:bar:13:foo')

        user_config_dir = os.path.join(default_config_dir, 'user')
        config = Config(default_config_dir)
        config.add_override_dir(user_config_dir)
        config = process_config(config, self.arg, args, flags)
        self.assertEqual(config.get('CHAIN_SPEC'), 'foo:foo:666:foo')

        config = Config(default_config_dir)
        config = process_config(config, self.arg, args, flags)
        self.assertEqual(config.get('CHAIN_SPEC'), 'baz:bar:13:foo')

        ap = ArgumentParser()
        process_args(ap, self.arg, flags)
        argv = [
                '-n',
                'user',
                ]
        args = ap.parse_args(argv)
        config = Config(default_config_dir, namespace=args.namespace)
        config = process_config(config, self.arg, args, flags)
        self.assertEqual(config.get('CHAIN_SPEC'), 'foo:foo:666:foo')


    def test_all_args(self):
        ap = ArgumentParser()
        flags = self.flags.all
        process_args(ap, self.arg, flags)

        args = ap.parse_args([
            '-y', 'foo',
            '-i', 'foo:bar:42:baz',
            ])

        config = Config()
        config = process_config(config, self.arg, args, flags)


if __name__ == '__main__':
    unittest.main()
