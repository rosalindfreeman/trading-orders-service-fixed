from fastapi import HTTPException, status

from app.models import Order
from app.repositories import DuplicateOrderError, OrderRepository
from app.schemas import OrderCreate


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    async def submit(self, owner_id: str, request: OrderCreate) -> Order:
        try:
            return await self.repository.create(owner_id, request)
        except DuplicateOrderError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="client_order_id already exists",
            ) from exc

    async def retrieve(self, owner_id: str, order_id: str) -> Order:
        order = await self.repository.get(owner_id, order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def list(self, owner_id: str, limit: int, offset: int) -> list[Order]:
        return await self.repository.list(owner_id, limit, offset)

    async def cancel(self, owner_id: str, order_id: str) -> Order:
        order = await self.repository.cancel(owner_id, order_id)
        if order is not None:
            return order
        existing = await self.repository.get(owner_id, order_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Order not found")
        raise HTTPException(status_code=409, detail=f"Order is already {existing.status.value}")

