# Select Date 
A calendar application where users can log in and mark dates using different colors.

This is a monorepo:
- `client/` - Next.js frontend. Mostly generated with AI and integrated with backend by me (authorization, API routes, request debouncing)
- `server/` - FastAPI backend. Fully implemented by me (authorization, persistence, migrations, cache and containerization)

## Technical stack
**Frontend**
- Next.js

**Backend**
- Python, FastAPI
- Auth0
- SQLite database
- SQLAlchemy + Alembic
- Redis cache

## How to start
### Auth0 setup
1. Create an Auth0 account at https://auth0.com/
2. Create an Auth0 Application (type: Regular Web Application)
3. In the Auth0 Application settings, add:
    - **Allowed Callback URLs**: `http://localhost:8000/api/v1/auth/login/callback`
    - **Allowed Logout URLs**: `http://localhost:3000`
    - **Allowed Web Origins**: `http://localhost:3000`
4. Create an Auth0 API
5. In the Auth0 API settings, set:
    - **Name**: select-date (or any name you want)
    - **Identifier**: any unique URL-like value, e.g. `https://select-date/api`
    - **JSON Web Token (JWT) Signing Algorithm**: RS256

### Environment variables
This project requires two local env files:
- frontend: `client/.env.local`
- backend: `server/.env`

#### Create the file `client/.env.local`
Set the following variables:
- **AUTH0_SECRET**: any long random string (you can generate one with `openssl rand -hex 32`)
- **AUTH0_DOMAIN**: your Auth0 tenant domain as a URL from Auth0 Application settings, e.g. `http://<YOUR_AUTH0_DOMAIN>.us.auth0.com`
- **AUTH0_CLIENT_ID**: *Client ID* from your Auth0 Application settings
- **AUTH0_CLIENT_SECRET**: *Client Secret* from your Auth0 Application settings (keep it secret!)
- **AUTH0_AUDIENCE**: *Identifier* from your Auth0 API settings

#### Create the file `server/.env`
Set the following variables:
- **AUTH0_DOMAIN**: the same value as in `client/.env.local`
- **AUTH0_JWKS_PATH**: /.well-known/jwks.json
- **AUTH0_AUDIENCE**: the same value as in `client/.env.local`
- **AUTH0_ALGORITHM**: RS256
- **AUTH0_CLIENT_ID**: the same value as in `client/.env.local`
- **AUTH0_CLIENT_SECRET**: the same value as in `client/.env.local`
- **AUTH0_SCOPE**: openid profile email
- **AUTH0_REDIRECT_PATH**: /auth/login/callback
- **AUTH0_TOKEN_PATH**: /oauth/token
- **AUTH0_AUTHORIZE_PATH**: /authorize
- **AUTH0_LOGOUT_PATH**: /v2/logout

### Run application with Docker
Execute the following commands from the project root directory:
1. Build images: `docker compose build`
2. Run migrate: `docker compose run --rm migrate`
3. Start all services in the background: `docker compose up -d`
4. Stop application: `docker compose down`
