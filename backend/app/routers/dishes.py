import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_restaurant_for_owner, parse_images, save_upload
from app.models import Category, Dish, Restaurant
from app.schemas import DishCreate, DishOut, DishUpdate

router = APIRouter(prefix="/restaurants/{restaurant_id}/dishes", tags=["dishes"])


@router.get("", response_model=list[DishOut])
async def list_dishes(
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dish).where(Dish.restaurant_id == restaurant.id).order_by(Dish.sort_order, Dish.id)
    )
    return [DishOut.from_orm_dish(d) for d in result.scalars().all()]


@router.post("", response_model=DishOut)
async def create_dish(
    data: DishCreate,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    cat_result = await db.execute(
        select(Category).where(Category.id == data.category_id, Category.restaurant_id == restaurant.id)
    )
    if not cat_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Invalid category")

    dish = Dish(
        restaurant_id=restaurant.id,
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        price=data.price,
        images=json.dumps(data.images),
        is_hit=data.is_hit,
        is_hidden=data.is_hidden,
        sort_order=data.sort_order,
    )
    db.add(dish)
    await db.commit()
    await db.refresh(dish)
    return DishOut.from_orm_dish(dish)


@router.patch("/{dish_id}", response_model=DishOut)
async def update_dish(
    dish_id: int,
    data: DishUpdate,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Dish).where(Dish.id == dish_id, Dish.restaurant_id == restaurant.id))
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    update_data = data.model_dump(exclude_unset=True)
    if "images" in update_data:
        dish.images = json.dumps(update_data.pop("images"))

    for field, value in update_data.items():
        setattr(dish, field, value)

    await db.commit()
    await db.refresh(dish)
    return DishOut.from_orm_dish(dish)


@router.delete("/{dish_id}")
async def delete_dish(
    dish_id: int,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Dish).where(Dish.id == dish_id, Dish.restaurant_id == restaurant.id))
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    await db.delete(dish)
    await db.commit()
    return {"ok": True}


@router.post("/{dish_id}/images", response_model=DishOut)
async def upload_dish_image(
    dish_id: int,
    file: UploadFile = File(...),
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Dish).where(Dish.id == dish_id, Dish.restaurant_id == restaurant.id))
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    url = await save_upload(file)
    images = parse_images(dish.images)
    images.append(url)
    dish.images = json.dumps(images)

    await db.commit()
    await db.refresh(dish)
    return DishOut.from_orm_dish(dish)


@router.delete("/{dish_id}/images/{index}", response_model=DishOut)
async def delete_dish_image(
    dish_id: int,
    index: int,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Dish).where(Dish.id == dish_id, Dish.restaurant_id == restaurant.id))
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    images = parse_images(dish.images)
    if 0 <= index < len(images):
        images.pop(index)
    dish.images = json.dumps(images)

    await db.commit()
    await db.refresh(dish)
    return DishOut.from_orm_dish(dish)
