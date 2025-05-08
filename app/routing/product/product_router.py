from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.product_service.product_service import ProductService
from typing import List, Optional
import json

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    image: UploadFile = File(None),
    session: AsyncSession = Depends(get_session)
):
    product_service = ProductService(session)
    try:
        product = await product_service.create_product(
            name=name,
            price=price,
            description=description,
            image=image
        )
        return product
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating product: {str(e)}"
        )

@router.get("/{product_id}")
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session)
):
    product_service = ProductService(session)
    try:
        product = await product_service.get_product(product_id)
        return product
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting product: {str(e)}"
        )

@router.get("/")
async def get_all_products(
    session: AsyncSession = Depends(get_session)
):
    product_service = ProductService(session)
    try:
        products = await product_service.get_all_products()
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting products: {str(e)}"
        )