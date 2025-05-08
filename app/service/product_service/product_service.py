import os
import uuid
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Product
from typing import Optional
from pathlib import Path

class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.upload_dir = "uploads/products"
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)

    async def _save_image(self, file: UploadFile) -> str:
        """Сохраняет изображение товара и возвращает полный URL"""
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поддерживаются только изображения"
            )

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.png', '.jpg', '.jpeg']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неподдерживаемый формат изображения"
            )

        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = Path(self.upload_dir) / filename

        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return f"http://212.20.53.169:13299/uploads/products/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при сохранении изображения: {str(e)}"
            )
    
    async def create_product(
        self,
        name: str,
        price: float,
        description: Optional[str] = None,
        image: UploadFile = None
    ) -> Product:
        """Создает новый товар с изображением"""
        image_url = await self._save_image(image) if image else None

        product = Product(
            Name=name,
            Price=price,
            Description=description,
            Photo=image_url
        )

        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product


    async def get_product(self, product_id: int) -> Product:
        """Получает товар по ID"""
        product = await self.session.get(Product, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден"
            )
        return product

    async def get_all_products(self) -> list[Product]:
        """Получает все товары"""
        result = await self.session.execute(select(Product))
        return result.scalars().all()