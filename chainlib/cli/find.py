# standard imports
import sys
import os
import logging
from importlib import import_module

logg = logging.getLogger(__name__)


__mf = {}

def execute_for_path(d, fltr=None, cmd=None, args=None, handler=None):
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
    m = import_module(s + '._clf')
    handler(m, cmd, args)


def find_chainlib_modules(fltr=None, cmd=None, args=None, handler=None):
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
            r = execute_for_path(dp, fltr=fltr, cmd=cmd, args=args, handler=handler)
            if r != None:
                m.append(r)
    return m
