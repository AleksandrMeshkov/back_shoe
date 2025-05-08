from pydantic import BaseModel
from typing import Optional

class ProductCreateRequest(BaseModel):
    Name: str
    Price: float
    Description: Optional[str] = None

class ProductUpdateRequest(BaseModel):
    Name: Optional[str] = None
    Price: Optional[float] = None
    Description: Optional[str] = None

class ProductResponse(BaseModel):
    ProductID: int
    Name: str
    Price: float
    Description: Optional[str] = None
    Photo: Optional[str] = None

    class Config:
        from_attributes = True