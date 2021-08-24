class Signer:

    def sign_transaction(self):
        raise NotImplementedError()


    def sign_transaction_to_wire(self):
        raise NotImplementedError()


    def sign_message(self):
        raise NotImplementedError()

    
    def sign_message_to_wire(self):
        raise NotImplementedError()
