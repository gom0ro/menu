from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import generate_slug
from app.database import get_db
from app.deps import get_restaurant_for_owner
from app.models import Category, Restaurant
from app.schemas import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/restaurants/{restaurant_id}/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
async def list_categories(
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Category).where(Category.restaurant_id == restaurant.id).order_by(Category.sort_order)
    )
    return result.scalars().all()


@router.post("", response_model=CategoryOut)
async def create_category(
    data: CategoryCreate,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    category = Category(
        restaurant_id=restaurant.id,
        name=data.name,
        slug=generate_slug(data.name),
        sort_order=data.sort_order,
        is_active=data.is_active,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.restaurant_id == restaurant.id)
    )
    category = result.scalar_one_or_none()
    if not category:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Category not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "name" and value:
            category.slug = generate_slug(value)
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.restaurant_id == restaurant.id)
    )
    category = result.scalar_one_or_none()
    if not category:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.commit()
    return {"ok": True}
