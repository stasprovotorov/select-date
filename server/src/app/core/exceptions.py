class ApplicationBaseError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)
        

class BadRequestError(ApplicationBaseError):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message, status_code)


class UnauthorizedError(ApplicationBaseError):
    def __init__(self, message: str, status_code: int = 401) -> None:
        super().__init__(message, status_code)


class NotFoundError(ApplicationBaseError):
    def __init__(self, message: str, status_code: int = 404) -> None:
        super().__init__(message, status_code)


class UnprocessableEntityError(ApplicationBaseError):
    def __init__(self, message: str, status_code: int = 422) -> None:
        super().__init__(message, status_code)


class NotImplementedError(ApplicationBaseError):
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message, status_code)


class ServiceUnavailableError(ApplicationBaseError):
    def __init__(self, message: str, status_code: int = 503) -> None:
        super().__init__(message, status_code)
