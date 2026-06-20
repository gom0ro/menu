import json
import os
import uuid
import io
from pathlib import Path

from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from PIL import Image
import pillow_heif

# Register HEIF opener so Pillow can open .heic files directly
pillow_heif.register_heif_opener()

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
    # Superadmin can access any restaurant
    if user.email == "admin@menu.local":
        result = await db.execute(
            select(Restaurant).where(Restaurant.id == restaurant_id)
        )
    else:
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

    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = upload_dir / filename

    try:
        image = Image.open(io.BytesIO(content))
        
        # Ensure image is in RGB format for JPEG saving
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        # Resize image to save bandwidth and storage
        image.thumbnail((1200, 1200))
        
        image.save(filepath, "JPEG", quality=85)
    except Exception as e:
        print(f"Image processing error: {e}")
        # Fallback to saving raw bytes
        with open(filepath, "wb") as f:
            f.write(content)

    return f"/uploads/{filename}"
