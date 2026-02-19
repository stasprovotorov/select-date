import logging
import jwt
import jwt.exceptions as jwt_exceptions
from jwt.algorithms import RSAAlgorithm

from src.app.core.config import settings
from src.app.core import exceptions as app_exceptions

logger = logging.getLogger(__name__)


def validate_jwt(token: str, jwks: dict) -> dict:
    public_key = None
    unverified_header = jwt.get_unverified_header(token)
    jwt_kid = unverified_header.get("kid")

    if not jwt_kid:
        logger.error("No key ID found in JWT header")
        raise app_exceptions.NotFoundError("No key ID found in JWT header")
    logger.info("Retrieved key ID from JWT header")

    keys = jwks.get("keys")

    for jwk in keys:
        jwk: dict
        jwk_kid = jwk.get("kid")

        if jwt_kid == jwk_kid:
            try:
                public_key = RSAAlgorithm.from_jwk(jwk)
                logger.info("Retrieved public key from JWK")
                break
            except jwt_exceptions.InvalidKeyError as err:
                logger.exception("Failed to deserialize public key from JWK")
                raise app_exceptions.UnprocessableEntityError("Failed to retrieve public key") from err

    if not public_key:
        logger.error("No matching key ID found between JWT and JWKS")
        raise app_exceptions.NotFoundError("No matching JWK was found in JWKS")

    try:
        payload = jwt.decode(
            jwt=token,
            key=public_key,
            algorithms=settings.AUTH0_ALGORITHM,
            audience=settings.AUTH0_CLIENT_ID,
            issuer=settings.AUTH0_DOMAIN.encoded_string(),
            leeway=5,
        )
        logger.info("JWT successfully decoded")
        return payload
    except Exception as err:
        logger.exception("Failed to decode JWT")
        raise app_exceptions.UnprocessableEntityError("Failed to decode JWT") from err
