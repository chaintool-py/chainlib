# standard imports
import copy
import re


def is_valid_label(v, alpha_only=False):
    re_m = None
    if alpha_only:
        re_m = r'^[a-zA-Z]+$'
    else:
        re_m = r'^[a-zA-Z0-9]+$'
    return re.match(re_m, v)


class ChainSpec:
    """Encapsulates a 3- to 4-part chain identifier, describing the architecture used and common name of the chain, along with the network id of the connected network.

    The optional fourth field can be used to add a description value, independent of the chain identifier value.

    :param engine: Chain architecture
    :type engine: str
    :param common_name: Well-known name of chain
    :type common_name: str
    :param network_id: Chain network identifier
    :type network_id: int
    :param tag: Descriptive tag
    :type tag: str
    """
    def __init__(self, arch, fork, network_id, common_name=None, custom=[], safe=True):
        if custom == None:
            custom = []
        elif not isinstance(custom, list):
            raise ValueError('custom value must be list')

        self.o = {
        'arch': arch,
        'fork': fork,
        'network_id': network_id,
        'common_name': common_name,
        'custom': custom,
        }

        if safe:
            self.validate()


    def validate(self):
        self.o['network_id'] = int(self.o['network_id'])
        if not is_valid_label(self.o['arch'], alpha_only=True):
            raise ValueError('arch: ' + self.o['arch'])
        if not is_valid_label(self.o['fork'], alpha_only=True):
            raise ValueError('fork: ' + self.o['fork'])
        if self.o.get('common_name') and not is_valid_label(self.o['common_name']):
            raise ValueError('common_name: ' + self.o['common_name'])
        if self.o.get('custom'):
            for i, v in enumerate(self.o['custom']):
                if not is_valid_label(v):
                    raise ValueError('common_name {}: {}'.format(i, v))


    def network_id(self):
        """Returns the network id part of the spec.

        :rtype: int
        :returns: network_id
        """
        return self.o['network_id']


    def chain_id(self):
        """Alias of network_id

        :rtype: int
        :returns: network_id
        """
        return self.o['network_id']


    def engine(self):
        """Alias of self.arch()
        """
        return self.arch()


    def arch(self):
        """Returns the chain architecture part of the spec

        :rtype: str
        :returns: engine
        """
        return self.o['arch']


    def fork(self):
        """Returns the fork part of the spec

        :rtype: str
        :returns: fork
        """
        return self.o['fork']


    def common_name(self):
        """Returns the common name part of the spec

        :rtype: str
        :returns: common_name
        """
        return self.o['common_name']


    def is_same_as(self, chain_spec_cmp, use_common_name=False, use_custom=False):
        a = ['arch', 'fork', 'network_id']
        if use_common_name:
            a += ['common_name']
        if use_custom:
            a += ['custom']
        try:
            for k in a:
                assert(chain_spec_cmp.o[k] == self.o[k])
        except AssertionError:
            return False
        return True
                


    @staticmethod
    def from_chain_str(chain_str):
        """Create a new ChainSpec object from a colon-separated string, as output by the string representation of the ChainSpec object.

        String must be in one of the following formats:

        - <engine>:<common_name>:<network_id>
        - <engine>:<common_name>:<network_id>:<tag>

        :param chain_str: Chainspec string
        :type chain_str: str
        :raises ValueError: Malformed chain string
        :rtype: chainlib.chain.ChainSpec
        :returns: Resulting chain spec
        """
        o = chain_str.split(':')
        if len(o) < 3:
            raise ValueError('Chain string must have three sections, got {}'.format(len(o)))
        common_name = None
        if len(o) > 3:
            common_name = o[3]
        custom = []
        if len(o) > 4:
            for i in range(4, len(o)):
                custom.append(o[i])
        return ChainSpec(o[0], o[1], int(o[2]), common_name=common_name, custom=custom)


    @staticmethod
    def from_dict(o):
        """Create a new ChainSpec object from a dictionary, as output from the asdict method.

        The chain spec is described by the following keys:

        - engine
        - common_name
        - network_id
        - tag (optional)

        :param o: Chainspec dictionary
        :type o: dict
        :rtype: chainlib.chain.ChainSpec
        :returns: Resulting chain spec
        """
        return ChainSpec(o['arch'], o['fork'], o['network_id'], common_name=o.get('common_name'), custom=o.get('custom'))

  
    def asdict(self, use_common_name=True, use_custom=True):
        """Create a dictionary representation of the chain spec.

        :rtype: dict
        :returns: Chain spec dictionary
        """
        r = copy.copy(self.o)
        if not use_common_name:
            del r['common_name']
            del r['custom']
        if not use_custom:
            del r['custom']
        return r


    def as_string(self, skip_optional=False):
        s = '{}:{}:{}'.format(self.o['arch'], self.o['fork'], self.o['network_id'])
        if skip_optional:
            return s

        if self.o.get('common_name'):
            s += ':' + self.o['common_name']
        if self.o.get('custom'):
            s += ':' + ':'.join(self.o['custom'])
        return s


    def __str__(self):
        return self.as_string()        
