import logging
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
from src.app.core import exceptions

logger = logging.getLogger(__name__)


def validate_jwt(token: str, jwks: dict) -> dict:
    public_key = None

    unverified_header = jwt.get_unverified_header(token)
    kid_jwt = unverified_header.get("kid")

    if not kid_jwt:
        logger.error("No 'kid' found in the JWT header.")
        raise exceptions.NotFoundError("The key 'kid' was not found in the JWT's header.")
    logger.info("Received 'kid' from the JWT header.")

    keys = jwks.get("keys")

    for jwk in keys:
        kid_jwk = jwk.get("kid")

        if kid_jwt == kid_jwk:
            try:
                public_key = RSAAlgorithm.from_jwk(jwk)
                logger.info("Public key retrieved from JWK.")
            except InvalidKeyError as error:
                logger.error("Failed to obtain public key from JWT.")
                raise exceptions.UnprocessableEntityError("Failed to obtain the public key from JWK.") from error

    if not public_key:
        logger.error("No matching 'kid' found between the JWT and the JWKS.")
        raise exceptions.NotFoundError("No JWK was found for the given JWKS.")

    try:
        payload = jwt.decode(
            jwt=token,
            key=public_key,
            algorithms=settings.AUTH0_ALGORITHM,
            audience=settings.AUTH0_CLIENT_ID,
            issuer=settings.AUTH0_DOMAIN.encoded_string(),
            leeway=5
        )
        logger.info("JWT successfully decoded.")
        return payload
    except (TypeError, DecodeError, InvalidAlgorithmError, InvalidAudienceError, InvalidIssuerError) as error:
        logger.error("Failed to decode the JWT.", exc_info=True)
        raise exceptions.UnprocessableEntityError("Failed to decode JWT.") from error
