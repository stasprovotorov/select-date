from src.app.core.exceptions import ApplicationBaseError


class DatabaseBaseError(ApplicationBaseError):
    def __init__(self, message: str = "Internal Server Error.", status_code: int = 500) -> None:
        super().__init__(message, status_code)


class DatabaseDateNotFoundError(DatabaseBaseError):
    def __init__(self, message: str = "Specified date not found for the user.") -> None:
        super().__init__(message)


class DatabaseGetDatesError(DatabaseBaseError):
    def __init__(self, message: str = "Failed to retrieve dates for the user from database.") -> None:
        super().__init__(message)
