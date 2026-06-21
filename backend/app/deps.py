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
import cloudinary
import cloudinary.uploader
import asyncio

# Register HEIF opener so Pillow can open .heic files directly
pillow_heif.register_heif_opener()

from app.auth import decode_token, get_user_by_email
from app.config import settings
from app.database import get_db
from app.models import Restaurant, User

security = HTTPBearer(auto_error=False)

if settings.cloudinary_cloud_name and settings.cloudinary_api_key and settings.cloudinary_api_secret:
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


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
    content = await file.read()
    if len(content) > settings.max_upload_size:
        raise HTTPException(status_code=400, detail="File too large")

    try:
        image = Image.open(io.BytesIO(content))
        
        # Ensure image is in RGB format for JPEG saving
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        # Resize image to save bandwidth and storage
        image.thumbnail((1200, 1200))
        
        buf = io.BytesIO()
        image.save(buf, "JPEG", quality=85)
        upload_content = buf.getvalue()
        
        if settings.cloudinary_cloud_name:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: cloudinary.uploader.upload(upload_content, folder="menu", resource_type="image")
            )
            return response['secure_url']
            
    except Exception as e:
        print(f"Image processing/upload error: {e}")
        
    # Fallback to local disk if Cloudinary fails or is not configured
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = upload_dir / filename
    
    with open(filepath, "wb") as f:
        # Just save the raw bytes if processing failed
        f.write(content)

    return f"/uploads/{filename}"
