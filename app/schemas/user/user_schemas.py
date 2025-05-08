from pydantic import BaseModel
from typing import Optional

class UserAuth(BaseModel):
    Login: str
    Password: str

class UserRegistration(BaseModel):
    Login: str
    Password: str
    Name: str
    Surname: str
    Patronymic: Optional[str] = None



class UserUpdate(BaseModel):
    Login: Optional[str] = None
    Password: Optional[str] = None
    Name: Optional[str] = None
    Surname: Optional[str] = None
    Patronymic: Optional[str] = None
    Photo: Optional[str] = None
