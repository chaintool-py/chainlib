class FeeOracle:

    def __init__(self, code_callback=None):
        self.code_callback = code_callback


    def get_fee(self, code_data=None, input_data=None, *args, **kwargs):
        raise NotImplementedError()
