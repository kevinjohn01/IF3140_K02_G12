from transaction import Transaction

class Schedule:
    def __init__(self,  type: str, data_item: str, transaction: Transaction):
        self.transaction = transaction
        self.data_item = data_item
        self.type = type