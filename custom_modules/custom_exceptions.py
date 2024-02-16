class EntryNotFound(Exception):
    pass

class ClassificationError(Exception):
    pass

class TextSplitError(Exception):
    pass

class TransmuterNotAvailable(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)