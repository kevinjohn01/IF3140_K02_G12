from core.mvcc import MultiversionTimestampOrderingCC
from core.occ import OptimisticCC
from utils.input_parser import InputParser
from tplocking import TPLocking


class Bootstrap:
    def __init__(self) -> None:
        parser = InputParser()

        cc_option = parser.read_cc_option()
        data = parser.read_file()

        match cc_option:
            case 1:
                twopl = TPLocking(data)
                twopl.run()
                pass
            case 2:
                occ = OptimisticCC(data)
                occ.run()
                pass
            case 3:
                mvcc = MultiversionTimestampOrderingCC(data)
                mvcc.run()
                pass
