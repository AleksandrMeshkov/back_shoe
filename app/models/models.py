from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"

    UsersID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Name: Mapped[str] = mapped_column(String(100))
    Surname: Mapped[str] = mapped_column(String(100))
    Patronymic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    Login: Mapped[str] = mapped_column(String(50), unique=True)
    Password: Mapped[str] = mapped_column(String(255))  # Рекомендую хранить хэш пароля
    Photo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Путь к фото

    baskets: Mapped[list["Basket"]] = relationship("Basket", back_populates="user")


class Product(Base):
    __tablename__ = "Products"

    ProductID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Name: Mapped[str] = mapped_column(String(100))
    Price: Mapped[float] = mapped_column(Float)
    Description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    Photo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Путь к фото товара

    baskets: Mapped[list["Basket"]] = relationship("Basket", back_populates="product")


class Basket(Base):
    __tablename__ = "Baskets"

    BasketID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    UsersID: Mapped[int] = mapped_column(Integer, ForeignKey("Users.UsersID"))
    ProductID: Mapped[int] = mapped_column(Integer, ForeignKey("Products.ProductID"))

    user: Mapped["User"] = relationship("User", back_populates="baskets")
    product: Mapped["Product"] = relationship("Product", back_populates="baskets")