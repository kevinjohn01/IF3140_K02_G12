import time
from typing import Dict, List, Set, Tuple


class MultiversionTimestampOrderingCC:
    def __init__(self, data: List[List[str]]) -> None:
        self.operations = data
        self.tx_ts_start: Dict[str, float] = {}
        self.resources: Dict[str, Dict[int, Dict[str, str | float]]] = {}
        self.tx_recent_operation: Dict[str, List[List[str]]] = {}
        self.reads: Set[Tuple[str, str]] = set()
        self.final_schedule: List[str] = []

    def run(self) -> None:
        print()
        self.__process_operation(self.operations, False)
        print()
        print('[✅] final schedule: ', end='')
        for _, operation in enumerate(self.final_schedule):
            print(operation, end=' ')
        print()

    def __process_operation(self, operations: List[List[str]], rolled_back: bool):
        for _, operation in enumerate(operations):
            time.sleep(1e-7)

            action = operation[0]
            tx = operation[1]

            if not self.tx_ts_start.get(tx) or rolled_back:
                self.tx_ts_start[tx] = time.time()
                if not rolled_back:
                    self.tx_recent_operation[tx] = []

            if action != 'C':
                resource_name = operation[2]
                if not self.resources.get(resource_name):
                    self.resources[resource_name] = {
                        0: {
                            'tx_producer': '0',
                            'rts': 0,
                            'wts': 0,
                            'content': '0'
                        }
                    }

            if not rolled_back:
                self.tx_recent_operation[tx].append(operation)

            match action:
                case 'W':
                    resource_name = operation[2]
                    content = operation[3]

                    for version in range(len(self.resources[resource_name]) - 1, -1, -1):
                        if float(self.resources[resource_name][version]['wts']) < self.tx_ts_start[tx]:
                            # if rts < ts(tx): create new version for the corresponding resource
                            if float(self.resources[resource_name][version]['rts']) > self.tx_ts_start[tx]:
                                self.__rollback(tx)

                            # rollback condition
                            else:
                                self.resources[resource_name][version + 1] = {
                                    'tx_producer': tx,
                                    'rts': self.tx_ts_start[tx],
                                    'wts': self.tx_ts_start[tx],
                                    'content': content
                                }

                                print(f'[✨] [TX-{tx}] [WRITE] {resource_name} v{version + 1} = {
                                    self.resources[resource_name][version + 1]}')

                                self.final_schedule.append(
                                    f'W{tx}({resource_name})')

                            break

                        elif abs(float(self.resources[resource_name][version]['wts']) - self.tx_ts_start[tx]) < 1e-9:
                            self.resources[resource_name][version]['content'] = content
                            self.resources[resource_name][version]['tx_producer'] = tx

                            print(f'[✨] [TX-{tx}] [WRITE] {resource_name} v{version} = {
                                self.resources[resource_name][version]}')

                            self.final_schedule.append(
                                f'W{tx}({resource_name})')

                            break

                case 'R':
                    resource_name = operation[2]

                    for version in range(len(self.resources[resource_name]) - 1, -1, -1):
                        if float(self.resources[resource_name][version]['wts']) < self.tx_ts_start[tx] or abs(float(self.resources[resource_name][version]['wts']) - self.tx_ts_start[tx]) < 1e-9:
                            self.resources[resource_name][version]['rts'] = self.tx_ts_start[tx]
                            self.reads.add(
                                (tx, str(self.resources[resource_name][version]['tx_producer'])))

                            print(f'[✨] [TX-{tx}] [READ] {resource_name} v{version} = {
                                self.resources[resource_name][version]}')

                            self.final_schedule.append(
                                f'R{tx}({resource_name})')

                            break

                case 'C':
                    print(f'[✨] [TX-{tx}] [COMMIT]')

                    self.final_schedule.append(f'C{tx}')

    def __rollback(self, tx: str) -> None:
        rolled_back_txs = self.__get_rolled_back_transaction(tx)
        for _, tx in enumerate(rolled_back_txs):
            print(f'[✨] [TX-{tx}] [ROLLBACK] start')
            self.final_schedule.append(f'Rb{tx}')
            self.__process_operation(self.tx_recent_operation[tx], True)
            print(f'[✨] [TX-{tx}] [ROLLBACK] end')

    def __get_rolled_back_transaction(self, tx: str) -> List[str]:
        result = [tx]
        new_reads: Set[Tuple[str, str]] = set()
        for _, read in enumerate(self.reads):
            if (read[1] == tx):
                result += self.__get_rolled_back_transaction(read[0])
            else:
                new_reads.add(read)

        self.reads = new_reads
        return result
