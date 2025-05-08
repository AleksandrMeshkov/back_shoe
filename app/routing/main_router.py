from fastapi import FastAPI, APIRouter
from app.routing.users.users_router import router as user_router
from app.routing.product.product_router import router as product_router
#from app.routing.basket.basket_router import router as basket_router  # Импортируем роутер для событий

# Создаем главный роутер с префиксом /v1
main_router = APIRouter(
    prefix="/v1"
)

main_router.include_router(user_router, tags=["Users"])

main_router.include_router(product_router, tags=["Product"])

# Включаем роутер для событий
#main_router.include_router(basket_router, tags=["Basket"])  # Добавляем роутер для событий