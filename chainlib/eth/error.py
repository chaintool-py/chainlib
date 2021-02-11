class EthException(Exception):
    pass


class RevertEthException(EthException):
    pass


class DefaultErrorParser:

    def translate(self, error):
        return EthException('default parser code {}'.format(error))
