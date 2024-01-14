from enum import Enum


class LockState(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    FREE = "FREE"
