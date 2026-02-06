from src.app.core.exceptions import ApplicationBaseError


class AuthorizationBaseError(ApplicationBaseError):
    def __init__(self, message: str = "Unauthorized.", status_code: int = 401) -> None:
        super().__init__(message, status_code)


class AuthorizationStateNotMatchError(AuthorizationBaseError):
    def __init__(self, message: str = "Authorization states do not match.") -> None:
        super().__init__(message)


class AuthorizationGetSessionError(AuthorizationBaseError):
    def __init__(self, message: str = "Failed to obtain session object from the server.") -> None:
        super().__init__(message)


class AuthorizationSetSessionError(AuthorizationBaseError):
    def __init__(self, message: str = "Failed to set session object in the server.") -> None:
        super().__init__(message)


class AuthorizationDeleteSessionError(AuthorizationBaseError):
    def __init__(self, message: str = "Failed to delete session object from the server.") -> None:
        super().__init__(message)


class AuthorizationSessionNotFoundError(AuthorizationBaseError):
    def __init__(self, message: str = "Session was not found in the server.") -> None:
        super().__init__(message)


class AuthorizationSessionDeserializationError(AuthorizationBaseError):
    def __init__(self, message: str = "Failed to deserialize session object from the server.") -> None:
        super().__init__(message)


class AuthorizationSessionIDNotFoundError(AuthorizationBaseError):
    def __init__(self, message: str = "Session ID not found.") -> None:
        super().__init__(message)


class AuthorizationKIDNotFoundError(AuthorizationBaseError):
    def __init__(self, message: str = "The key 'kid' was not found in the JWT's header.") -> None:
        super().__init__(message)


class AuthorizationGetPublicKeyError(AuthorizationBaseError):
    def __init__(self, message: str = "Failed to obtain the public key from JWK.") -> None:
        super().__init__(message)


class AuthorizationJWKNotFoundError(AuthorizationBaseError):
    def __init__(self, message: str = "No JWK was found for the given JWKS.") -> None:
        super().__init__(message)


class AuthorizationJWTDecodeError(AuthorizationBaseError):
    def __init__(self, message: str = "Failed to decode JWT.") -> None:
        super().__init__(message)


class AuthorizationUnsuccessfulAuth0ResponseError(AuthorizationBaseError):
    def __init__(self, message: str = "Unsuccessful response code from Auth0 API.") -> None:
        super().__init__(message)
        

class AuthorizationJSONDecodeError(AuthorizationBaseError):
    def __init__(self, message: str = "Failed to decode response body to JSON.") -> None:
        super().__init__(message)


class AuthorizationTokenNotFoundError(AuthorizationBaseError):
    def __init__(self, message: str = "ID token not found in response body.") -> None:
        super().__init__(message)
