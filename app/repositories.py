from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, OrderStatus
from app.schemas import OrderCreate


class DuplicateOrderError(Exception):
    pass


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, owner_id: str, request: OrderCreate) -> Order:
        order = Order(owner_id=owner_id, **request.model_dump())
        self.session.add(order)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise DuplicateOrderError from exc
        await self.session.refresh(order)
        return order

    async def get(self, owner_id: str, order_id: str) -> Order | None:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id, Order.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def list(self, owner_id: str, limit: int, offset: int) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.owner_id == owner_id)
            .order_by(Order.created_at.desc(), Order.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars())

    async def cancel(self, owner_id: str, order_id: str) -> Order | None:
        result = await self.session.execute(
            update(Order)
            .where(
                Order.id == order_id,
                Order.owner_id == owner_id,
                Order.status == OrderStatus.OPEN,
            )
            .values(status=OrderStatus.CANCELLED)
            .returning(Order)
        )
        order = result.scalar_one_or_none()
        await self.session.commit()
        return order

