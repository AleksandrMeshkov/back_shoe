import os
import uuid
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Product
from typing import Optional
from pydantic import BaseModel

class ProductCreateRequest(BaseModel):
    Name: str
    Price: float
    Description: Optional[str] = None

class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.upload_dir = "uploads/products"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def _save_image(self, file: UploadFile) -> str:
        """Сохраняет изображение товара и возвращает имя файла"""
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поддерживаются только изображения"
            )

        file_ext = os.path.splitext(file.filename)[-1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, filename)

        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return filename
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при сохранении изображения: {str(e)}"
            )

    async def _delete_image(self, filename: str):
        """Удаляет изображение товара"""
        if filename:
            try:
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass  # Не блокируем выполнение если не удалось удалить файл

    async def create_product(
        self,
        product_data: ProductCreateRequest,
        image: UploadFile
    ) -> Product:
        """Создает новый товар с изображением"""
        image_filename = await self._save_image(image)

        product = Product(
            Name=product_data.Name,
            Price=product_data.Price,
            Description=product_data.Description,
            Photo=image_filename
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

    async def update_product(
        self,
        product_id: int,
        product_data: dict,
        image: Optional[UploadFile] = None
    ) -> Product:
        """Обновляет информацию о товаре"""
        product = await self.get_product(product_id)

        if image:
            await self._delete_image(product.Photo)
            product.Photo = await self._save_image(image)

        if product_data.get("Name") is not None:
            product.Name = product_data["Name"]
        if product_data.get("Price") is not None:
            product.Price = product_data["Price"]
        if product_data.get("Description") is not None:
            product.Description = product_data["Description"]

        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete_product(self, product_id: int):
        """Удаляет товар"""
        product = await self.get_product(product_id)
        await self._delete_image(product.Photo)
        await self.session.delete(product)
        await self.session.commit()