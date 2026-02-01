class DatabaseBaseError(Exception):
    pass


class DatabaseBatchOperationError(DatabaseBaseError):
    pass


class DatabaseGetDatesError(DatabaseBaseError):
    pass
