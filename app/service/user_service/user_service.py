from typing import Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile, status
from pathlib import Path
import uuid
from app.models.models import User
from app.schemas.user.user_schemas import UserAuth, UserRegistration, UserUpdate

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.UsersID == user_id))
        return result.scalars().first()

    async def get_user_by_login(self, login: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.Login == login))
        return result.scalars().first()

    async def register(self, user_data: UserRegistration) -> User:
        if await self.get_user_by_login(user_data.Login):
            raise HTTPException(status_code=400, detail="Login already exists")

        user = User(
            Login=user_data.Login,
            Password=user_data.Password,
            Name=user_data.Name,
            Surname=user_data.Surname,
            Patronymic=user_data.Patronymic
        )
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_profile(self, user_id: int, data: Dict[str, Any], photo_file: UploadFile = None):
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if photo_file:
            try:
                file_name = await self.save_uploaded_file(photo_file)
                full_photo_url = f"http://212.20.53.169:1211/uploads/{file_name}"
                data['Photo'] = full_photo_url  
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при обработке файла: {str(e)}"
                )

        update_fields = {k: v for k, v in data.items() if v is not None}

        if not update_fields:
            return existing_user  

        query = update(User).where(User.UsersID == user_id).values(**update_fields).returning(User)
        
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            updated_user = result.scalars().first()
            return updated_user
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении профиля: {str(e)}"
            )

    async def authenticate(self, auth_data: UserAuth) -> User:
        user = await self.get_user_by_login(auth_data.Login)
        if not user or auth_data.Password != user.Password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user

    async def upload_photo(self, user_id: int, photo: UploadFile) -> str:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        file_ext = Path(photo.filename).suffix.lower()
        if file_ext not in ['.png', '.jpg', '.jpeg']:
            raise HTTPException(status_code=400, detail="Invalid file type")

        filename = f"{uuid.uuid4()}{file_ext}"
        filepath = Path(f"uploads/{filename}")
        filepath.parent.mkdir(exist_ok=True)

        with open(filepath, "wb") as buffer:
            buffer.write(await photo.read())

        user.Photo = str(filepath)
        await self.session.commit()
        return str(filepath)
    
    @staticmethod
    async def save_uploaded_file(file: UploadFile, upload_dir: str = "uploads") -> str:
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя файла отсутствует"
            )
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.gif']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неподдерживаемый формат файла"
            )
        
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_path / file_name
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return file_name
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при сохранении файла: {str(e)}"
            )