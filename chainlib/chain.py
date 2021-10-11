# standard imports
import copy


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
    def __init__(self, arch, fork, network_id, common_name=None):
        self.o = {
                'arch': arch,
                'fork': fork,
                'network_id': network_id,
                'common_name': common_name,
                }

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
        """Returns the chain architecture part of the spec

        :rtype: str
        :returns: engine
        """
        return self.o['arch']


    def common_name(self):
        """Returns the common name part of the spec

        :rtype: str
        :returns: common_name
        """
        return self.o['common_name']


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
        if len(o) == 4:
            common_name = o[3]
        return ChainSpec(o[0], o[1], int(o[2]), common_name)


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
        return ChainSpec(o['arch'], o['fork'], o['network_id'], common_name=o['common_name'])

  
    def asdict(self):
        """Create a dictionary representation of the chain spec.

        :rtype: dict
        :returns: Chain spec dictionary
        """
        return copy.copy(self.o)


    def __str__(self):
        s = '{}:{}:{}'.format(self.o['arch'], self.o['fork'], self.o['network_id'])
        if self.o['common_name'] != None:
            s += ':' + self.o['common_name']
        return s
