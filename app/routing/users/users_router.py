from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.user_service.user_service import UserService
from app.schemas.user.user_schemas import UserAuth, UserRegistration, UserUpdate
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/register")
async def register(
    request: UserRegistration,
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)
    user = await user_service.register(request)
    return {"message": "User created successfully", "user_id": user.UsersID}

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)
    auth_data = UserAuth(Login=form_data.username, Password=form_data.password)
    user = await user_service.authenticate(auth_data)
    return user

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    request: UserUpdate = Depends(),
    photo_file: UploadFile = File(None),
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)
    
    update_data = request.dict(exclude_unset=True)
    
    if photo_file:
        try:
            file_name = await UserService.save_uploaded_file(photo_file)
            full_photo_url = f"http://212.20.53.169:1211/uploads/{file_name}"
            update_data["Photo"] = full_photo_url
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": f"Ошибка при загрузке файла: {str(e)}"}
            )
    
    user = await user_service.update_profile(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": "User updated successfully",
        "user": user
    }