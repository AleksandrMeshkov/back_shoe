from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status
from app.models.models import Basket, Product
from sqlalchemy.orm import selectinload

class BasketService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_to_basket(self, user_id: int, product_id: int) -> Basket:
        """Добавляет товар в корзину пользователя"""
        # Проверяем существует ли товар
        product = await self.session.get(Product, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден"
            )

        # Проверяем нет ли уже этого товара в корзине
        existing_item = await self.session.execute(
            select(Basket)
            .where(Basket.UsersID == user_id)
            .where(Basket.ProductID == product_id)
        )
        if existing_item.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товар уже в корзине"
            )

        # Добавляем товар в корзину
        basket_item = Basket(UsersID=user_id, ProductID=product_id)
        self.session.add(basket_item)
        await self.session.commit()
        await self.session.refresh(basket_item)
        return basket_item

    async def get_user_basket(self, user_id: int) -> List[Basket]:
        """Получает все товары в корзине пользователя"""
        result = await self.session.execute(
            select(Basket)
            .where(Basket.UsersID == user_id)
            .options(selectinload(Basket.product))  # Загружаем связанный товар
        )
        return result.scalars().all()

    async def remove_from_basket(self, user_id: int, product_id: int) -> None:
        """Удаляет товар из корзины пользователя"""
        result = await self.session.execute(
            delete(Basket)
            .where(Basket.UsersID == user_id)
            .where(Basket.ProductID == product_id)
        )
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден в корзине"
            )
        await self.session.commit()

    async def clear_basket(self, user_id: int) -> None:
        """Очищает корзину пользователя"""
        await self.session.execute(
            delete(Basket)
            .where(Basket.UsersID == user_id)
        )
        await self.session.commit()