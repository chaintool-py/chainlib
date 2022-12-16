class DialectFilter:

    def apply_block(self, block):
        return block


    def apply_tx(self, tx):
        return tx


    def apply_result(self, result):
        return result


    def apply_src(self, src):
        return src


    def validate_src(self, src):
        return src
