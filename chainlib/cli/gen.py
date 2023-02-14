# standard imports
import sys
import os
import logging
from importlib import import_module

logg = logging.getLogger(__name__)


__mf = {}

# to fulfill this protocol, the module MUST:
# * include a file MODULE/data/.chainlib 
# * must export the method args(v) in the root module namespace. It must return the argument keys recognized by the command v, two arrays in a tuple, where the first array includes required argument keys and the second includes optional keys. If the command recognizes no arguments, an empty tuple should be returned.

def execute_for_path(d, fltr=None, cmd=None, args=None, handler=None, is_key_query=False):
    logg.debug('scanning package directory {}'.format(d))
    fp = os.path.join(d, 'data', '.chainlib')
    if not os.path.exists(fp):
        return None
    s = os.path.basename(d)
    if fltr != None and s not in fltr:
        logg.info('skipped chainlib module "{}" not matching search filter'.format(s))
        return None
    pm = __mf.get(s)
    if pm != None:
        logg.info('skipped chainlib module "{}" already exxcuted from {}'.format(s, pm))
        return None
    __mf[s] = d
    logg.info('found chainlib module {} in {}'.format(s, d))
    m = import_module(s)
    handler(m, cmd, args, is_key_query=is_key_query)


def find_chainlib_modules(fltr=None, cmd=None, args=None, handler=None, is_key_query=False):
    m = []
    for p in sys.path:
        logg.debug('scanning path is {}'.format(p))
        (n, x) = os.path.splitext(p)
        if x:
            continue
        for d in os.listdir(p):
            dp = os.path.join(p, d)
            if not os.path.isdir(dp):
                continue
            r = execute_for_path(dp, fltr=fltr, cmd=cmd, args=args, handler=handler, is_key_query=is_key_query)
            if r != None:
                m.append(r)
    return m
