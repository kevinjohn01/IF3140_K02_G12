curr_timestamp = 1

class Transaction:
    def __init__(self,transaction_id: int, timestamp: int = curr_timestamp) -> None:
        global curr_timestamp
        self.transaction_id = transaction_id
        self.lock = set()
        self.timestamp = timestamp
        self.state = None
        self.OperationList = []
        curr_timestamp += 1

    def assign_lock(self,data_item,type) -> None:
        self.lock.add(data_item)

    def delete_lock(self,data_item):
        self.lock.discard(data_item)

    def addOperationList(self,operation, data_item) -> None:
        self.OperationList.append([operation,data_item])

    def __repr__(self) -> str:
        return f"transaction_id: {self.transaction_id}\nlock list: {self.lock}\ntimestamp: {self.timestamp}\nstate:{self.state}"

# class DataItem:
#     def __init__(self, data_item):
#         self.dataitemid = data_item
#         self.transaction = []
#         self.locktype = None
class Schedule:
    def __init__(self,  type: str, data_item: str, transaction: Transaction):
        self.transaction = transaction
        self.data_item = data_item
        self.type = type

class TwoPhaseLocking():
    def __init__(self):
        self.lockTable = {}
        self.queue = []
        self.schedule = []
        self.dataItemList = []
        self.transaction = []

    def shared_lock(self,transaction: Transaction,data_item):
        if data_item not in self.lockTable.keys():
            self.initiate_lock(data_item)
        
        data = self.lockTable[data_item]

        if (data['state'] == 'unlocked' or (data['state'] == 'S' and self.acquireSharedLock(transaction,data_item))):
            data['state'] = 'S'
            data['transactions'].add(transaction.transaction_id)
            transaction.assign_lock(data_item,'S')
            self.addSchedule(transaction.transaction_id,data_item,'S')

        else:
            self.queue.append((transaction.transaction_id,'S',data_item))

            #Wound wait
            if self.wound_wait(transaction, self.getHoldingTransaction(data_item)):
                self.abort(transaction)
            else:
                transaction.state = 'w'

    def exclusive_lock(self, transaction: Transaction, data_item):
        if data_item not in self.lockTable.keys():
            self.initiate_lock(data_item)
        
        data = self.lockTable[data_item]

        #No transaction lock the data item
        if (data['state'] == 'unlocked' and not self.hasSharedLock(data_item)):
            data['state'] = 'X'
            data['transactions'].add(transaction.transaction_id)
            transaction.assign_lock(data_item,'X')
            self.addSchedule(transaction.transaction_id,data_item,'X')

        #upgrade lock from shared lock to exclusive lock
        elif (self.hasSharedLock(data_item) and len(data['transactions']) == 1 and next(iter(data['transactions'])) == transaction.transaction_id ):
            print(f"lock {data_item} upgraded to exclusive lock")
            data['state'] = 'X'
            transaction.delete_lock(data_item)
            transaction.assign_lock(data_item,'X')
            self.addSchedule(transaction.transaction_id,data_item,'X')

        #Others
        else:
            self.queue.append((transaction,'X',data_item))

            #Wound wait
            if self.wound_wait(transaction, self.getHoldingTransaction(data_item)):
                self.abort(transaction)
            else:
                print(f"Transaction {transaction.transaction_id} waiting...")
                transaction.state = 'w'

    def addSchedule(self,transaction_id,data_item,type):
        sch = Schedule(type,data_item,transaction_id)
        self.schedule.append(sch)

    def initiate_lock(self,data_item):
        self.lockTable[data_item] = {
            'state': 'unlocked',
            'transactions': set(),
        }
    
    def unlock(self,transaction:Transaction,data_item) -> None:
        if data_item in self.lockTable:
            data = self.lockTable[data_item]
            data['transactions'].discard(transaction.transaction_id)
            transaction.lock.discard((transaction.transaction_id, 'X'or'S',data_item))
            if not data['transactions']:
                data['state'] = 'unlocked'
                self.checkQueue(data_item)

    def hasSharedLock(self, data_item) -> bool:
        return (self.lockTable[data_item]['state'] == 'S')  
    
    def hasExclusiveLock(self, data_item) -> bool:
        return self.lockTable[data_item]['state'] == 'X'
    
    def acquireSharedLock(self, transaction: Transaction,data_item):
        return not (self.hasExclusiveLock(data_item)) or self.hasSharedLock(data_item)

    def commit(self,transaction):
        transaction.state = 'committed'
        print(f"Transaction {transaction.transaction_id} commited")
        for data_item in transaction.lock:
            self.unlock(transaction,data_item)
            self.checkQueue(data_item)
        

    def abort(self,transaction: Transaction):
        transaction.state = 'aborted'
        print(f"Transaction {transaction.transaction_id} aborted")
        for data_item in transaction.lock:
            self.unlock(transaction,data_item)

        #Jalanin ulang transaksi
        self.rerun_transaction(transaction)

    def getHoldingTransaction(self,data_item):
        return next(iter(self.lockTable[data_item]['transactions']), None)
    
    def rerun_transaction(self,transaction:Transaction):
        for operation in transaction.OperationList:
            operator = operation[0]
            data_item = operation[1]
            self.lock(transaction,data_item,operator)
    
    def lock(self, transaction, data_item, operation):
        if (operation == 'R' or operation == 'S'):
            self.shared_lock(transaction,data_item)
        elif (operation == 'W' or operation == 'X'):
            self.exclusive_lock(transaction,data_item)

    def printSchedule(self):
        for sch in self.schedule:
            print(f"Lock-{sch.type}{sch.transaction}({sch.data_item})")

    def wound_wait(self,transaction: Transaction, holding_transaction_id):
        return holding_transaction_id is not None and transaction.transaction_id > holding_transaction_id
    
    def checkQueue(self,data_item):
        for i in range (len(self.queue)):
            if (self.queue[i][2] == data_item):
                self.lock(self.queue[i][0],self.queue[i][2],self.queue[i][1])

    def __repr__(self) -> str:
        pass

if __name__ == '__main__':
    ccm = TwoPhaseLocking()
    t1 = Transaction(1)
    t2 = Transaction(2)
    #ccm.exclusive_lock(t2,"a")
    ccm.shared_lock(t1,"b")
    ccm.shared_lock(t2,"b")
    ccm.exclusive_lock(t1,"b")
    ccm.exclusive_lock(t2,"a")
    
    #ccm.shared_lock(t2,"b")
    # print(ccm.queue)
    # print(t2)
    # print(t1)
    ccm.commit(t2)
    ccm.printSchedule()
