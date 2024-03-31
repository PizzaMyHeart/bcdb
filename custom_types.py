from enum import Enum, auto

class RawDataType(Enum):
    ARTICLE = auto()
    COMMENT = auto()


class EntryAlreadyExists(Exception):
    """Entry already exists in database."""