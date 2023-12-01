from transaction import Transaction
from schedule import Schedule
from collections import deque

class TPLocking:
    def __init__(self, data):
        self.lockTable = {}
        self.queue = deque()
        self.schedule = []
        self.transactions = []
        self.status = 'running'
        self.data = data

    def initiate_lock(self,data_item):
        self.lockTable[data_item] = {
            'state': 'unlocked',
            'transactions': set(),
        }

    def isQueue(self,transaction: Transaction) -> bool:
        found = False

        for x in self.queue:
            for data_item in self.lockTable:
                transaction_info = x[1]
                #print("yey",transaction_info)
                if(transaction_info != None):
                    if (transaction_info.transaction_id == transaction.transaction_id):
                        found = True
        return found
    
    def shared_lock(self, transaction: Transaction, data_item) -> bool:
        #data_item baru
        if data_item not in self.lockTable.keys():
            self.initiate_lock(data_item)
        
        data = self.lockTable[data_item]

        if (data['state'] == 'unlocked' or data['state'] == 'shared'):
            transaction.state = 'running'
            data['state'] = 'shared'
            data['transactions'].add(transaction.transaction_id)

            transaction.assign_lock(data_item,'S')
            transaction.addOperationList('S',data_item)
            self.schedule.append(['S',transaction.transaction_id,data_item])
            self.state = 'running'
            return True
        else:
            #Deadlock handling with wait-die mechanism
            if (transaction.state=='aborted' or self.state == 'rollback'):
                self.queue.append(['S',transaction,data_item])
                return False
            if (transaction.state == 'waiting' or self.state == 'queue'):
                return False
            if self.waitdie(transaction, self.getHoldingTransaction(data_item)):
                transaction.state = 'waiting'
                self.queue.append(['S',transaction,data_item])
            else:
                self.abort(transaction)
                self.shared_lock(transaction, data_item)
            self.state = 'running'
            return True

    def exclusive_lock(self,transaction: Transaction, data_item: str) -> bool:
        #data_item baru
        if data_item not in self.lockTable.keys():
            self.initiate_lock(data_item)
        
        data = self.lockTable[data_item]

        #No transaction locking data  item
        if (data['state'] == 'unlocked'):
            transaction.state = 'running'
            data['state'] = 'exclusive'
            data['transactions'].add(transaction.transaction_id)

            transaction.assign_lock(data_item,'X')
            transaction.addOperationList('X',data_item)
            self.schedule.append(['X',transaction.transaction_id,data_item])
            self.state = 'running'
            return True

        #Upgrade Lock
        elif (data['state'] == 'shared' and len(data['transactions']) == 1 and next(iter(data['transactions'])) == transaction.transaction_id):
            print(f"[!] lock {data_item} upgraded to exclusive lock")
            transaction.state = 'running'
            data['state'] = 'exclusive'

            transaction.delete_lock(data_item)
            transaction.assign_lock(data_item,'X')
            transaction.addOperationList('X', data_item)
            self.schedule.append(['X',transaction.transaction_id,data_item])
            self.state = 'running'
            return True
        #Other
        else:
            if ( transaction.state == 'aborted' or self.state == 'rollback'):
                self.queue.append(['X',transaction,data_item])
                return False
            if (transaction.state == 'waiting' or self.state=='queue'):
                return False
            #Deadlock handling with wait-die mechanism
            if self.waitdie(transaction, self.getHoldingTransaction(data_item)):
                transaction.state = 'waiting'
                self.queue.append(['X',transaction,data_item])
            else:
                self.abort(transaction)
                
                self.exclusive_lock(transaction, data_item)
            self.state = 'running'
            return False

    def commit(self, transaction: Transaction) -> None:
        if self.isQueue(transaction):
            #Cannot commit since operation is not completed
            self.queue.append(['C',transaction])
        else:
            print(f"Transaction {transaction.transaction_id} commited")

            #Commit transaction
            transaction.state = 'commited'
            self.schedule.append(['C',transaction.transaction_id])

            #Unlock all data item locked by transaction
            for x in transaction.lock:
                self.unlock(transaction, x[0])
            self.checkQueue()

    def abort(self, transaction: Transaction) -> None:
        #transaction aborted
        print(f"Transaction {transaction.transaction_id} aborted")
        transaction.state = 'aborted'
        self.state = 'rollback'

        print(transaction.state)
        self.schedule.append(['A',transaction.transaction_id])
        #Unlock data item hold by transaction
        for i in range (len(transaction.lock)):
            self.unlock(transaction,transaction.lock[i][0])
        
        #Jalankan ulang transaksi
        self.rerun_transaction(transaction)

    def rerun_transaction(self,transaction: Transaction):
        # stop = False
        # curr_ops = transaction.OperationList
        # while(stop == False and len(curr_ops) !=0):
        #     op = curr_ops.pop()
        #     print(f"op: {curr_ops}")
        #     if (op[0] == 'S' or op[0] == 'X' or op[0] == 'W' or op[0] == 'R'):
        #         status = self.lock(transaction,op[1],op[0])
        #         if not(status):
        #             #curr_ops.appendleft(op)
        #             stop = True
        #         print(f"op: {curr_ops}")
        #     elif (op[0] == 'C'):
        #         self.commit(transaction)
        #     elif (op[0] == 'A'):
        #         self.abort(transaction)
        #     else:
        #         print(f"[!] operasi gagal dijalankan")
        print(f"--------------MENJALANKAN TRANSAKSI {transaction.transaction_id} ULANG ------------------------")
        for op in transaction.OperationList:
            self.queue.append([op[0],transaction,op[1]])
            print(transaction.OperationList)
            print(f"queue setelah abort:{self.queue}")
        #self.checkQueue()
        print("-------------------------------SELESAI-----------------------------------------")

    def unlock(self, transaction: Transaction,data_item) :
        if data_item in self.lockTable.keys():
            data = self.lockTable[data_item]

            #remove lock from lockTable
            data['transactions'].discard(transaction.transaction_id)

            #remove lock from transaction
            transaction.delete_lock(data_item)

            #add to schedule
            self.schedule.append(['UL',transaction.transaction_id,data_item])

            #Run other transaction in queue if no transaction hold data item
            if not(data['transactions']):
                data['state']  = 'unlocked'
                # self.checkQueue()
            #transaction.addOperationList('UL', data_item)

    def waitdie(self, younger_transaction: Transaction, older_transaction_id):
        return older_transaction_id is not None and younger_transaction.transaction_id < older_transaction_id
    
    def getHoldingTransaction(self,data_item) -> str:
        return next(iter(self.lockTable[data_item]['transactions']), None)

    def checkQueue(self):
        print(f"--------------MENJALANKAN QUEUE ------------------------")
        self.state = 'queue'
        if (len(self.queue) != 0):
            stop =False
            while not(stop) and len(self.queue) != 0:
                curr_ops = self.queue.popleft()
                type = curr_ops[0]
                transaction = curr_ops[1]
                transaction.state = 'queue'
                if (len(curr_ops) == 2):
                    if type == 'C':
                        self.commit(transaction)
                        return
                elif len(curr_ops) == 3:
                    data_item = curr_ops[2]
                    status = self.lock(transaction,data_item,type)

                    print(self.queue)
                    if not(status):
                        print("\nyah gagal\n")
                        if curr_ops not in (self.queue):
                            self.queue.append(curr_ops)
                        print(self.queue)
                        stop = True
                    else:
                        print("\nyeah berhasil\n")

        print("-------------------------------SELESAI-----------------------------------------")

    #Ga mungkin berubah lagi
    def lookForTrx(self, trx_id):
        for trx in self.transactions:
            if trx.transaction_id == trx_id:
                return trx
        return None
    
    def lock(self, transaction, data_item, operation) -> bool:
        if (operation == 'R' or operation == 'S'):
            return self.shared_lock(transaction,data_item)
        elif (operation == 'W' or operation == 'X'):
            return self.exclusive_lock(transaction,data_item)
        else:
            raise Exception("Operation invalid!")
    
    def printSchedule(self):
        for sch in self.schedule:
            if(len(sch) == 2):
                print(f"{sch[0]}{sch[1]}")
            elif (len(sch) == 3):
                if (sch[0] == 'S' or sch[0] == 'X'):
                    print(f"Lock-{sch[0]}{sch[1]}({sch[2]})")
                else:
                    print(f"{sch[0]}{sch[1]}({sch[2]})")

    def run(self):
        for op in self.data:
            # try:
            print(op)
            #self.checkQueue()

            if (len(op) == 2):
                trx = self.lookForTrx(op[1])
                if (trx == None):
                    raise Exception("Unknown transaction request to be commited")
                if (op[0] == 'C'):
                    self.commit(trx)
                else:
                    print("Operation invalid!")
                
            elif(len(op) == 5):
                #Initialize
                ops = op[0]
                trx = self.lookForTrx(op[1])
                if trx==None:
                    trx = Transaction(op[1])
                    self.transactions.append(trx)
                data = op[3]
                #Classified which action will be taken
                status = self.lock(trx,data,ops)
            print(f"queue: {self.queue}")
            # except Exception as e:
            #     print(e)
            #     continue
        print(self.queue)
        self.checkQueue()
        self.printSchedule()

    def __repr__(self):
        pass


if __name__ == '__main__':
    ccm = TPLocking([])
    seq = input("Type the sequence: ")
    seq_filtered = seq.replace(" ","").split(";")
    ccm.data = seq_filtered
    ccm.run()