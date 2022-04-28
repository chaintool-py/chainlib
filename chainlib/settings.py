# local imports
from .chain import ChainSpec


class ChainSettings:

    def __init__(self, include_sync=False, include_queue=False):
        self.o = {}
        self.get = self.o.get


    def process_common(self, config):
        self.o['CHAIN_SPEC'] = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))


    def process(self, config):
        self.process_common(config)


    def __str__(self):
        ks = list(self.o.keys())
        ks.sort()
        s = ''
        for k in ks:
            s += '{}: {}\n'.format(k, self.o.get(k))
        return s
