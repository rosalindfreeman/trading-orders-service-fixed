from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import authenticated_subject, create_access_token, valid_client_credentials
from app.db import get_session
from app.repositories import OrderRepository
from app.schemas import OrderCreate, OrderPage, OrderResponse, TokenRequest, TokenResponse
from app.services import OrderService

router = APIRouter()


def get_order_service(session: AsyncSession = Depends(get_session)) -> OrderService:
    return OrderService(OrderRepository(session))


@router.post("/auth/token", response_model=TokenResponse, tags=["authentication"])
async def issue_token(request: TokenRequest, settings: Settings = Depends(get_settings)) -> TokenResponse:
    if not valid_client_credentials(request.client_id, request.client_secret, settings):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token, expires_in = create_access_token(request.client_id, settings)
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.post("/orders", response_model=OrderResponse, status_code=201, tags=["orders"])
async def submit_order(
    request: OrderCreate,
    subject: str = Depends(authenticated_subject),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return OrderResponse.model_validate(await service.submit(subject, request))


@router.get("/orders/{order_id}", response_model=OrderResponse, tags=["orders"])
async def retrieve_order(
    order_id: str,
    subject: str = Depends(authenticated_subject),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return OrderResponse.model_validate(await service.retrieve(subject, order_id))


@router.get("/orders", response_model=OrderPage, tags=["orders"])
async def list_orders(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    subject: str = Depends(authenticated_subject),
    service: OrderService = Depends(get_order_service),
) -> OrderPage:
    items = await service.list(subject, limit, offset)
    return OrderPage(items=[OrderResponse.model_validate(item) for item in items], limit=limit, offset=offset)


@router.delete("/orders/{order_id}", response_model=OrderResponse, tags=["orders"])
async def cancel_order(
    order_id: str,
    subject: str = Depends(authenticated_subject),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return OrderResponse.model_validate(await service.cancel(subject, order_id))

