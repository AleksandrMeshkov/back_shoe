from app.service.basket_service.basket_service import BasketService
from app.database.database import get_session

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix = "/basket"
)

@router.get("/get_all_basket")
async def get_all_basket(user_id: int, session: AsyncSession = Depends(get_session)):
    result = await BasketService(session).get_user_basket(user_id)
    return result


@router.post("/add_to_basket")
async def add_to_basket(user_id: int, product_id: int, session: AsyncSession = Depends(get_session)):
    result = await BasketService(session).add_to_basket(user_id, product_id)
    return result


@router.delete("/delete_from_basket")
async def delete_from_basket(user_id: int, product_id: int, session: AsyncSession = Depends(get_session)):
    result = await BasketService(session).remove_from_basket(user_id, product_id)
    return result