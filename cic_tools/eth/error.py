class EthException(Exception):
    pass


class DefaultErrorParser:

    def translate(self, error):
        return EthException('default parser code {}'.format(error))
