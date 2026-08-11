from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import OrderStatus, OrderType, Side


class TokenRequest(BaseModel):
    client_id: str = Field(min_length=1, max_length=128)
    client_secret: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class OrderCreate(BaseModel):
    client_order_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    symbol: str = Field(min_length=1, max_length=16, pattern=r"^[A-Za-z0-9.-]+$")
    side: Side
    order_type: OrderType
    quantity: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    limit_price: Decimal | None = Field(default=None, gt=0, max_digits=20, decimal_places=8)

    @model_validator(mode="after")
    def price_matches_order_type(self) -> "OrderCreate":
        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("limit_price is required for LIMIT orders")
        if self.order_type == OrderType.MARKET and self.limit_price is not None:
            raise ValueError("limit_price must be omitted for MARKET orders")
        self.symbol = self.symbol.upper()
        return self


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_order_id: str
    symbol: str
    side: Side
    order_type: OrderType
    quantity: Decimal
    limit_price: Decimal | None
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderPage(BaseModel):
    items: list[OrderResponse]
    limit: int
    offset: int

