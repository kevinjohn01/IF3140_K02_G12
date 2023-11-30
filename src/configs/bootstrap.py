from utils.input_parser import InputParser


class Bootstrap:
    def __init__(self) -> None:
        parser = InputParser()

        cc_option = parser.read_cc_option()
        print(cc_option)

        data = parser.read_file()
        print(data)
