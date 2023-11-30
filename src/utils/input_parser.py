from io import TextIOWrapper
from multiprocessing import Value
import re
from typing import List, Tuple

from configs.common import CC_OPTIONS, ROOT_DIR
from configs.error import InvalidCCChoice, InvalidFileInputFormat
from configs.schedule import ACTION_LIST


class InputParser:
    def __init__(self) -> None:
        self.file_name: str = ''
        self.file: TextIOWrapper
        self.data: List[List[str]] = []
        self.cc_option: int

    def read_cc_option(self) -> int:
        while True:
            try:
                print()
                print('CC Options:')
                for key, value in CC_OPTIONS.items():
                    print(f'{key}: {value}')
                self.cc_option = int(input('[🚀] choose cc (e.g. 1): ').strip())
                valid, message = self.__validate_cc_option()
                if not valid:
                    raise InvalidCCChoice(message)
                break
            except ValueError:
                print('[❗] invalid cc choice. provide the correct one (e.g. 1)')
            except InvalidCCChoice as e:
                print(f'[❗] {e.error}')

        return self.cc_option

    def __validate_cc_option(self) -> Tuple[bool, str]:
        if self.cc_option not in CC_OPTIONS.keys():
            return (False, 'invalid cc choice. provide the correct one (e.g. 1)')
        return (True, '')

    def read_file(self) -> List[List[str]]:
        while True:
            try:
                print()
                self.file_name = input('[🚀] input file name: ').strip()
                with open(f'{ROOT_DIR}/test/{self.file_name}', 'r') as self.file:
                    self.__parse()
                    valid, line, message = self.__validate_file()
                    if not valid:
                        raise InvalidFileInputFormat(line, message)
                break
            except IsADirectoryError:
                print(f'[❗] {self.file_name} not found. provide another file')
            except FileNotFoundError:
                print(f'[❗] {self.file_name} not found. provide another file')
            except InvalidFileInputFormat as e:
                print(f'[❗] {e.error}')

        return self.data

    def __validate_file(self) -> Tuple[bool, int, str]:
        if len(self.data) == 0:
            return (False, 1, 'no content')

        for i, line in enumerate(self.data):
            if len(line) < 2 or len(line) > 3:
                return (False, i + 1, 'invalid structure')
            if line[0] not in ACTION_LIST:
                return (False, i + 1, 'invalid action')
            if line[0] == 'C' and len(line) != 2:
                return (False, i + 1, 'invalid structure')
            if line[0] != 'C' and len(line) == 2:
                return (False, i + 1, 'invalid structure')
            if not re.fullmatch(r"^(?![0])[0-9]+$", line[1]):
                return (False, i + 1, 'invalid transaction name')
            if len(line) > 2:
                if line[0] == 'O' and not re.fullmatch(r"^[A-Za-z]+=[0-9]+$", line[2]):
                    return (False, i + 1, 'invalid resource name')
                if line[0] != 'O' and not re.fullmatch(r"^[A-Za-z]+$", line[2]):
                    return (False, i + 1, 'invalid operation structure')

        return (True, -1, '')

    def __parse(self) -> None:
        if self.file:
            lines = self.file.read().splitlines()
            for line in lines:
                self.data.append(line.strip().split(' '))