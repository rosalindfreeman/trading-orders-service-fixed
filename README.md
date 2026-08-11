# Trading Orders Service

I developed a secure Python trade-order API using FastAPI. I used Pydantic validation to prevent malformed orders and introduced authentication and clear separation between API and business logic. For production I would use PostgreSQL rather than in-memory storage, Redis for frequently accessed data, secret management rather than hard-coded credentials, TLS, rate limiting and multiple container instances behind a load balancer.



An asynchronous Python API for securely submitting, retrieving, listing, and cancelling orders. The code separates HTTP handlers, business services, repositories, and database models so exchange/execution logic can evolve independently.

## Windows quick start

Install Python 3.12 if needed:

```powershell
winget install --id Python.Python.3.12 -e
```

Close and reopen PowerShell, extract this package, and run these commands from the extracted folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup-windows.ps1
.\run-windows.ps1
```

The scripts deliberately use `.venv\Scripts\python.exe` for installation and startup. This prevents `ModuleNotFoundError` errors caused by installing packages into one Python interpreter and starting the API with another.

Open `http://localhost:8000/docs` after startup.

## Manual local setup

```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

SQLite is used when `DATABASE_URL` is unset. For the production-like PostgreSQL setup:

```bash
docker compose up --build --scale api=2
```

Put a load balancer or ingress in front of the replicas. The service stores no session state, so any authenticated request can reach any replica.

## API example

Obtain a short-lived JWT:

```bash
curl -X POST http://localhost:8000/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id":"demo-trader","client_secret":"demo-secret"}'
```

PowerShell:

```powershell
$tokenResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/v1/auth/token" `
  -ContentType "application/json" `
  -Body '{"client_id":"demo-trader","client_secret":"demo-secret"}'

$token = $tokenResponse.access_token
```

Then use the returned token:

```bash
curl -X POST http://localhost:8000/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"client_order_id":"alpha-001","symbol":"AAPL","side":"BUY","order_type":"LIMIT","quantity":"10","limit_price":"200.50"}'
```

PowerShell (using `$token` from the previous example):

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/v1/orders" `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"client_order_id":"alpha-001","symbol":"AAPL","side":"BUY","order_type":"LIMIT","quantity":"10","limit_price":"200.50"}'
```

Endpoints are documented at `/docs`:

- `POST /v1/auth/token`
- `POST /v1/orders`
- `GET /v1/orders`
- `GET /v1/orders/{id}`
- `DELETE /v1/orders/{id}`
- `GET /health/live` and `GET /health/ready`

## Production notes

- Replace the demonstration client credentials and JWT secret using a secret manager. The `/auth/token` endpoint models client-credentials authentication; production deployments can instead validate tokens issued by an external identity provider.
- PostgreSQL pooling is controlled by `DB_POOL_SIZE` and `DB_MAX_OVERFLOW`. Size the total across all replicas below the database connection limit.
- The unique `(owner_id, client_order_id)` constraint safely rejects retry duplicates across replicas. Cancellation is a conditional atomic update, preventing competing replicas from cancelling the same open order twice.
- JSON logs include request ID, route, response status, and duration. Incoming `X-Request-ID` is echoed for tracing.
- Schema creation on startup is convenient for this example. Use Alembic migrations under a deployment job before rolling out production replicas.

## Test

```bash
pytest
```

Install test dependencies first when using the manual setup:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest
```
