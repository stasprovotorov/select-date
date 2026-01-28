from fastapi.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED


class UserNotAuthorized(HTTPException):
    def __init__(self, detail="User is not authorized."):
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class AuthStatesNotMatched(HTTPException):
    def __init__(self, detail="Authorization states do not match."):
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST, 
            detail=detail
        )


class AuthTokenError(HTTPException):
    def __init__(self, detail="User is not authorized."):
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED, 
            detail=detail
        )


class TokenValidationError(HTTPException):
    def __init__(self, detail):
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Failed to validate token: {detail}"
        )


class AuthBaseError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class AuthSessionError(AuthBaseError):
    def __init__(self, *args):
        super().__init__(*args)


class AuthSessionGetError(AuthSessionError):
    def __init__(self):
        super().__init__("Failed to obtain session object from the server.")


class AuthSessionSetError(AuthSessionError):
    def __init__(self):
        super().__init__("Failed to set session object in the server.")


class AuthSessionDeleteError(AuthSessionError):
    def __init__(self):
        super().__init__("Failed to remove session object from the server.")


class AuthSessionDeserializationError(AuthSessionError):
    def __init__(self):
        super().__init__("Failed to deserialize session object from the server.")
