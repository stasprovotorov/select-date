import os
from dotenv import load_dotenv
from typing import Annotated
import json
import jwt
from aiohttp import ClientSession, ClientError, TCPConnector
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()
APP_ENV = os.getenv("APP_ENV")
DOMAIN = os.getenv("AUTH0_DOMAIN")
AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = os.getenv("AUTH0_ALGORITHMS")
JWKS = os.getenv("AUTH0_JWKS")

security = HTTPBearer()


class AuthError(HTTPException):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail


async def fetch_jwks(url: str) -> dict:
    """Fetch JWKS from the Auth0 API"""

    connector = None
    if APP_ENV == "development":
        connector = TCPConnector(ssl=False)

    try:
        async with ClientSession(connector=connector) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise AuthError(401, f"Failed to obtain JWKS from Auth0: HTTP {resp.status}")
                jwks = await resp.json(content_type=None)
                return jwks
    except json.JSONDecodeError as err:
        raise AuthError(401, "Invalid JWKS JSON") from err
    except ClientError as err:
        raise AuthError(401, "Failed to obtain JWKS from Auth0") from err


async def requires_auth(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """JSON Web Token validation"""
    
    if not all([DOMAIN, AUDIENCE, ALGORITHMS, JWKS]):
        raise AuthError(401, "Missing required config variable(s)")

    token = credentials.credentials
    jwks = await fetch_jwks(JWKS)
    unverified_header = jwt.get_unverified_header(token)

    jwt_kid = unverified_header.get("kid")
    if not jwt_kid:
        raise AuthError(401, 'Missing "kid" (key ID) in JWT header')
    
    public_key = None
    is_jwk_found = False

    for jwk in jwks["keys"]:
        if jwk["kid"] == jwt_kid:
            try:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                is_jwk_found = True
                break
            except Exception as err:
                raise AuthError(401, "Failed to create PSA public key from JWK") from err

    if not is_jwk_found:
        raise AuthError(401, "Unable to find JWK for JWT kid")

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=ALGORITHMS,
            audience=AUDIENCE,
            issuer=DOMAIN,
            leeway=5
        )
        return payload
    except jwt.ExpiredSignatureError as err:
        raise AuthError(401, "Token is expired") from err
    except jwt.InvalidAudienceError as err:
        raise AuthError(401, "Incorrect audience, please check the audience") from err
    except jwt.InvalidIssuerError as err:
        raise AuthError(401, "Incorrect issuer, please check the issuer") from err
    except Exception as err:
        raise AuthError(401, "Unable to parse authentication token") from err
