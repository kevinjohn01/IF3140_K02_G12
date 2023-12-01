curr_timestamp = 1
from collections import deque

class Transaction:
    def __init__(self,transaction_id: int, timestamp: int = curr_timestamp) -> None:
        global curr_timestamp
        self.transaction_id = transaction_id
        self.lock = []
        self.timestamp = timestamp
        self.state = None
        self.OperationList = deque()
        curr_timestamp += 1

    def assign_lock(self,data_item,type) -> None:
        self.lock.append([data_item,type])

    def delete_lock(self,data_item):
        if (len(self.lock) != 0):
            i = 0
            while i<len(self.lock):
                print("i=", i)
                print("len=", len(self.lock))
                if self.lock[i][0] == data_item:
                    self.lock = self.lock[0:i-1] + self.lock[i+1:len(self.lock)]
                i += 1

    def addOperationList(self,operation, data_item) -> None:
        print(f"Operasi T{self.transaction_id} {operation} pada {data_item} berhasil ditambahkan")
        self.OperationList.append([operation,data_item])

    def getOperation(self):
        return self.OperationList.pop()

    def discardOperationGet(self,operation, data_item):
        self.OperationList.appendLeft([operation,data_item])

    def __repr__(self) -> str:
        return f"transaction_id: {self.transaction_id}\nlock: {self.lock}"