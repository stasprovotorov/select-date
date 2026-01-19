from fastapi.exceptions import HTTPException


class DatabaseError(HTTPException):
    """
    HTTPException subclass for database related errors.
    """
    def __init__(self, status_code: int = 500, detail: str = "Internal database error"):
        super().__init__(status_code=status_code, detail=detail)
