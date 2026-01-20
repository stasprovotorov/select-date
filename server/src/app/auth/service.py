import jwt
from jwt.algorithms import RSAAlgorithm
from src.app.auth.config import settings as auth_settings
from src.app.auth.exceptions import TokenValidationError


def validate_jwt(token: str, jwks: set) -> dict:
    public_key = None

    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    if not kid:
        TokenValidationError("The key 'kid' was not found in the token's header.")

    for jwk in jwks:
        if kid == jwk["kid"]:
            try:
                public_key = RSAAlgorithm.from_jwk(jwk)
            except Exception as err:
                TokenValidationError(str(err))

    if not public_key:
        TokenValidationError("No JWK was found for the given 'kid'.")

    try:
        payload = jwt.decode(
            jwt=token,
            key=public_key,
            algorithms=auth_settings.ALGORITHM,
            audience=auth_settings.CLIENT_ID,
            issuer=auth_settings.DOMAIN,
            leeway=5
        )
        return payload
    except Exception as err:
        raise TokenValidationError(str(err))
    