import json
import os
import uuid
from pathlib import Path

from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import decode_token, get_user_by_email
from app.config import settings
from app.database import get_db
from app.models import Restaurant, User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await get_user_by_email(db, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_restaurant_for_owner(
    restaurant_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Restaurant:
    result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id, Restaurant.owner_id == user.id)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


def parse_images(images_str: str) -> list[str]:
    try:
        return json.loads(images_str) if images_str else []
    except json.JSONDecodeError:
        return []


async def save_upload(file: UploadFile) -> str:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    if len(content) > settings.max_upload_size:
        raise HTTPException(status_code=400, detail="File too large")

    ext = Path(file.filename or "image.jpg").suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        ext = ".jpg"

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = upload_dir / filename
    with open(filepath, "wb") as f:
        f.write(content)

    return f"/uploads/{filename}"
