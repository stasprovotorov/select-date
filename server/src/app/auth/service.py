import jwt
from jwt.algorithms import RSAAlgorithm
from jwt.exceptions import (
    DecodeError, 
    InvalidKeyError, 
    InvalidAlgorithmError, 
    InvalidAudienceError, 
    InvalidIssuerError
)

from src.app.core.settings import settings
from src.app.auth.exceptions import (
    AuthTokenKidNotFoundError, 
    AuthTokenPublicKeyError, 
    AuthTokenJwkNotFoundError, 
    AuthTokenJwtDecodeError
)


def validate_jwt(token: str, jwks: dict) -> dict:
    public_key = None

    unverified_header = jwt.get_unverified_header(token)
    kid_jwt = unverified_header.get("kid")

    if not kid_jwt:
        # Log it.
        raise AuthTokenKidNotFoundError
    
    keys = jwks.get("keys")

    if keys:
        for jwk in keys:
            kid_jwk = jwk.get("kid")

            if kid_jwt == kid_jwk:
                try:
                    public_key = RSAAlgorithm.from_jwk(jwk)
                    # Log it.
                except InvalidKeyError as error:
                    # Log it.
                    raise AuthTokenPublicKeyError from error

    if not keys or not public_key:
        # Log it.
        raise AuthTokenJwkNotFoundError

    try:
        payload = jwt.decode(
            jwt=token,
            key=public_key,
            algorithms=settings.AUTH0_ALGORITHM,
            audience=settings.AUTH0_CLIENT_ID,
            issuer=settings.AUTH0_DOMAIN.encoded_string(),
            leeway=5
        )
        # Log it.
        return payload
    except (TypeError, DecodeError, InvalidAlgorithmError, InvalidAudienceError, InvalidIssuerError) as error:
        # Log it.
        raise AuthTokenJwtDecodeError from error
