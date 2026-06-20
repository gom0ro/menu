import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_restaurant_for_owner, parse_images, save_upload
from app.models import Category, Dish, ModifierGroup, ModifierOption, Restaurant
from app.schemas import (
    DishCreate,
    DishOut,
    DishUpdate,
    ModifierGroupCreate,
    ModifierGroupOut,
    ModifierOptionCreate,
    ModifierOptionOut,
)

router = APIRouter(prefix="/restaurants/{restaurant_id}/dishes", tags=["dishes"])


@router.get("", response_model=list[DishOut])
async def list_dishes(
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dish)
        .where(Dish.restaurant_id == restaurant.id)
        .options(selectinload(Dish.modifier_groups).selectinload(ModifierGroup.options))
        .order_by(Dish.sort_order, Dish.id)
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


# --- Modifiers ---

@router.post("/{dish_id}/modifiers", response_model=ModifierGroupOut)
async def create_modifier_group(
    dish_id: int,
    data: ModifierGroupCreate,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Dish).where(Dish.id == dish_id, Dish.restaurant_id == restaurant.id))
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    group = ModifierGroup(
        dish_id=dish.id,
        name=data.name,
        is_required=data.is_required,
        max_choices=data.max_choices,
    )
    db.add(group)
    await db.flush()

    for opt_data in data.options:
        opt = ModifierOption(
            group_id=group.id,
            name=opt_data.name,
            price_delta=opt_data.price_delta,
        )
        db.add(opt)

    await db.commit()
    result_group = await db.execute(
        select(ModifierGroup)
        .where(ModifierGroup.id == group.id)
        .options(selectinload(ModifierGroup.options))
    )
    return result_group.scalar_one()


@router.delete("/{dish_id}/modifiers/{group_id}")
async def delete_modifier_group(
    dish_id: int,
    group_id: int,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Dish).where(Dish.id == dish_id, Dish.restaurant_id == restaurant.id))
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    result = await db.execute(select(ModifierGroup).where(ModifierGroup.id == group_id, ModifierGroup.dish_id == dish.id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Modifier group not found")

    await db.delete(group)
    await db.commit()
    return {"ok": True}

