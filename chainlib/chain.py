class ChainSpec:

    def __init__(self, engine, common_name, network_id, tag=None):
        self.o = {
                'engine': engine,
                'common_name': common_name,
                'network_id': network_id,
                'tag': tag,
                }

    def network_id(self):
        return self.o['network_id']


    def chain_id(self):
        return self.o['network_id']


    def engine(self):
        return self.o['engine']


    def common_name(self):
        return self.o['common_name']


    @staticmethod
    def from_chain_str(chain_str):
        o = chain_str.split(':')
        if len(o) < 3:
            raise ValueError('Chain string must have three sections, got {}'.format(len(o)))
        tag = None
        if len(o) == 4:
            tag = o[3]
        return ChainSpec(o[0], o[1], int(o[2]), tag)


    def __str__(self):
        s = '{}:{}:{}'.format(self.o['engine'], self.o['common_name'], self.o['network_id'])
        if self.o['tag'] != None:
            s += ':' + self.o['tag']
        return s
