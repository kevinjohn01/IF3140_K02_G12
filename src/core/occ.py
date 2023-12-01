from code import interact
import sys
import time
from typing import Dict, List


class OptimisticCC:
    def __init__(self, operations: List[List[str]]) -> None:
        self.operations = operations
        self.tx_timestamp: Dict[str, Dict[str, float]] = {}
        self.tx_written: Dict[str, set[str]] = {}
        self.tx_read: Dict[str, set[str]] = {}
        self.tx_resource: Dict[str, Dict[str, str]] = {}
        self.final_schedule: List[str] = []
        self.aborted: bool = False

    def run(self) -> None:
        print()
        for _, operation in enumerate(self.operations):
            time.sleep(1e-7)

            action = operation[0]
            tx = operation[1]

            if not self.tx_timestamp.get(tx):
                self.tx_timestamp[tx] = {
                    'start': time.time(), 'validation': float(sys.maxsize), 'end': float(sys.maxsize)
                }

            if abs(self.tx_timestamp[tx]["end"] - sys.maxsize) > 1e-9:
                print("[❗] invalid operation on input. aborting.")
                self.aborted = True
                break

            if not self.tx_resource.get(tx):
                self.tx_resource[tx] = {}

            match action:
                case 'W':
                    resource_name = operation[2]
                    resource_value = operation[3]

                    self.tx_resource[tx][resource_name] = resource_value

                    print(
                        f'[✨] [TX-{tx}] [WRITE] {resource_name} = {
                            self.tx_resource[tx][resource_name]}'
                    )

                    self.final_schedule.append(f'W{tx}({resource_name})')

                    if not self.tx_written.get(tx):
                        self.tx_written[tx] = {resource_name}
                        continue

                    self.tx_written[tx].add(resource_name)

                case 'R':
                    resource_name = operation[2]

                    if not self.tx_resource[tx].get(resource_name):
                        self.tx_resource[tx][resource_name] = '0'

                    print(
                        f'[️✨] [TX-{tx}] [READ] {resource_name} = {
                            self.tx_resource[tx][resource_name]}'
                    )

                    self.final_schedule.append(f'R{tx}({resource_name})')

                    if not self.tx_read.get(tx):
                        self.tx_read[tx] = {resource_name}
                        continue

                    self.tx_read[tx].add(resource_name)

                case 'C':
                    self.tx_timestamp[tx]["validation"] = time.time()

                    print(f'[✨] [TX-{tx}] [VALIDATE]')

                    self.final_schedule.append(f'V{tx}')

                    if not self.__validate(tx):
                        print(f'[✨] [TX-{tx}] [ROLLBACK]')

                        self.final_schedule.append(f'Rb{tx}')

                        self.__rollback(tx)
                    print(
                        f'[✨] [TX-{tx}] [FINISHED], final values: {self.tx_resource[tx]}')

                    self.final_schedule.append(f'C{tx}')

                    self.tx_timestamp[tx]["end"] = time.time()

        # print final schedule
        if not self.aborted:
            print()
            print('[✅] final schedule: ', end='')
            for i, operation in enumerate(self.final_schedule):
                print(f'{operation}', end=' ')
            print()

    def __validate(self, tx: str) -> bool:
        for timestamp_tx, timestamp_tx_value in self.tx_timestamp.items():
            if timestamp_tx != tx:
                if self.tx_timestamp[tx]["start"] < timestamp_tx_value["end"] < self.tx_timestamp[tx]["validation"]:
                    if self.tx_written.get(timestamp_tx) and self.tx_read[tx].intersection(self.tx_written[timestamp_tx]):
                        return False
        return True

    def __rollback(self, tx: str) -> None:
        self.tx_timestamp[tx] = {
            "start": time.time(),
            "validation": time.time(),
            "end": sys.maxsize
        }
