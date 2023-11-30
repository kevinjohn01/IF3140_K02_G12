class InvalidFileInputFormat(Exception):
    def __init__(self, line: int, message="invalid format") -> None:
        self.line = line
        self.message = message
        self.error = f'Error on line {line}, {message}'
        super().__init__(self.error)


class InvalidCCChoice(Exception):
    def __init__(self, message: str) -> None:
        self.error = message
        super().__init__(self.error)
