from typing import List


class OptimisticCC:
    def __init__(self, operations: List[List[str]]) -> None:
        self.operations = operations
        pass

    def run(self) -> None:
        for operation in enumerate(self.operations):
            print(operation)
