from pathlib import Path

ROOT_DIR = Path(__file__).absolute().parent.parent.parent
CC_OPTIONS = {
    1: 'Two-Phase Locking (2PL)',
    2: 'Optimistic Concurrency Control (OCC)',
    3: 'Multiversion Timestampt Ordering Concurrency Control (MVCC)'
}
ACTION_LIST = ['R', 'W', 'C']
