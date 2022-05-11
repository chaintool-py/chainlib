# standard imports
import unittest
import os
import logging

# external imports
from aiee.arg import process_args

# local imports
import chainlib.cli
#from chainlib.cli.base import argflag_std_base
from chainlib.cli.arg import (
        ArgFlag,
        Arg,
        ArgumentParser,
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
        config = chainlib.cli.config.Config.from_args(args, arg_flags=flags)
        self.assertEqual(config.get('CONFIG_USER_NAMESPACE'), 'foo')


    def test_args_process_schema_override(self):
        ap = chainlib.cli.arg.ArgumentParser()
        flags = self.flags.VERBOSE | self.flags.CONFIG
        process_args(ap, self.arg, flags)

        args = ap.parse_args([])

        config = chainlib.cli.config.Config.from_args(args, arg_flags=flags, base_config_dir=config_dir)
        self.assertEqual(config.get('FOO_BAR'), 'baz')


    def test_args_process_arg_override(self):
        ap = chainlib.cli.arg.ArgumentParser()
        flags = self.flags.VERBOSE | self.flags.CONFIG
        process_args(ap, self.arg, flags)

        argv = [
            '-c',
            config_dir,
            '-n',
            'foo',
            ]
        args = ap.parse_args(argv)
        config = chainlib.cli.config.Config.from_args(args, arg_flags=flags, base_config_dir=config_dir)
        self.assertEqual(config.get('FOO_BAR'), 'bazbazbaz')


    def test_args_process_internal_override(self):
        ap = chainlib.cli.arg.ArgumentParser()
        flags = self.flags.VERBOSE | self.flags.CONFIG
        process_args(ap, self.arg, flags)

        args = ap.parse_args()
        default_config_dir = os.path.join(config_dir, 'default')
        config = chainlib.cli.config.Config.from_args(args, arg_flags=flags, default_config_dir=default_config_dir)
        self.assertEqual(config.get('CHAIN_SPEC'), 'baz:bar:13:foo')

        user_config_dir = os.path.join(default_config_dir, 'user')
        config = chainlib.cli.config.Config.from_args(args, arg_flags=flags, default_config_dir=default_config_dir, user_config_dir=user_config_dir)
        self.assertEqual(config.get('CHAIN_SPEC'), 'foo:foo:666:foo')

        config = chainlib.cli.config.Config.from_args(args, arg_flags=flags, default_config_dir=default_config_dir, user_config_dir=default_config_dir)
        self.assertEqual(config.get('CHAIN_SPEC'), 'baz:bar:13:foo')

        ap = chainlib.cli.arg.ArgumentParser()
        process_args(ap, self.arg, flags)
        argv = [
                '-n',
                'user',
                ]
        args = ap.parse_args(argv)
        config = chainlib.cli.config.Config.from_args(args, arg_flags=flags, default_config_dir=default_config_dir, user_config_dir=default_config_dir)
        self.assertEqual(config.get('CHAIN_SPEC'), 'foo:foo:666:foo')


    def test_args_process_extra(self):
        ap = chainlib.cli.arg.ArgumentParser()
        flags = self.flags.VERBOSE | self.flags.CONFIG
        process_args(ap, self.arg, flags)
        ap.add_argument('--foo', type=str)
        argv = [
            '--foo',
            'bar',
                ]
        args = ap.parse_args(argv)
        extra_args = {
            'foo': None,
            }
        config = chainlib.cli.config.Config.from_args(args, arg_flags=flags, extra_args=extra_args)
        self.assertEqual(config.get('_FOO'), 'bar')

        extra_args = {
            'foo': 'FOOFOO',
            }
        config = chainlib.cli.config.Config.from_args(args, arg_flags=flags, extra_args=extra_args)
        self.assertEqual(config.get('FOOFOO'), 'bar')


if __name__ == '__main__':
    unittest.main()
