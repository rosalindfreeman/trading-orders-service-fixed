from httpx import AsyncClient


async def test_order_lifecycle(client: AsyncClient, auth_headers: dict[str, str]):
    payload = {
        "client_order_id": "strategy-42",
        "symbol": "aapl",
        "side": "BUY",
        "order_type": "LIMIT",
        "quantity": "12.5",
        "limit_price": "215.75",
    }
    created = await client.post("/v1/orders", json=payload, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["symbol"] == "AAPL"
    order_id = created.json()["id"]

    fetched = await client.get(f"/v1/orders/{order_id}", headers=auth_headers)
    assert fetched.status_code == 200

    listed = await client.get("/v1/orders", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()["items"]) == 1

    cancelled = await client.delete(f"/v1/orders/{order_id}", headers=auth_headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"

    repeated = await client.delete(f"/v1/orders/{order_id}", headers=auth_headers)
    assert repeated.status_code == 409


async def test_authentication_and_validation(client: AsyncClient, auth_headers: dict[str, str]):
    assert (await client.get("/v1/orders")).status_code == 401
    invalid = await client.post(
        "/v1/orders",
        headers=auth_headers,
        json={
            "client_order_id": "bad",
            "symbol": "AAPL",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": "0",
        },
    )
    assert invalid.status_code == 422


async def test_duplicate_client_order_id_is_rejected(client: AsyncClient, auth_headers: dict[str, str]):
    payload = {
        "client_order_id": "duplicate",
        "symbol": "MSFT",
        "side": "SELL",
        "order_type": "MARKET",
        "quantity": "1",
    }
    assert (await client.post("/v1/orders", json=payload, headers=auth_headers)).status_code == 201
    assert (await client.post("/v1/orders", json=payload, headers=auth_headers)).status_code == 409

