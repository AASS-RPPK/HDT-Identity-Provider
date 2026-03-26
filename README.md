# HDT Identity Provider (FastAPI)

This service handles authentication and token validation used by the API Gateway.

There is no screenshot for this service, so this README is based on the implemented code.

Gateway-routed auth endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/verify`
- `GET /auth/users`
- `GET /auth/users/{user_id}`

These are exposed through `HDT-API-Gateway` via `/auth/*`.

## Run

1. Install dependencies
   - `pip install -r requirements.txt`
2. Start the server
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Endpoints

### Register

`POST /auth/register`

Body (JSON):
```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "secret123"
}
```

### Login

`POST /auth/login`

Body (JSON):
```json
{
  "username": "john",
  "password": "secret123"
}
```

### Refresh token

`POST /auth/refresh`

Body (JSON):
```json
{
  "refresh_token": "..."
}
```

### Verify token (used by gateway)

`POST /auth/verify`

Body (JSON):
```json
{
  "token": "..."
}
```

