import io
import json

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import generate_short_code, generate_slug, hash_password
from app.database import get_db
from app.deps import get_current_user, get_restaurant_for_owner
from app.models import AnalyticsEvent, Category, Dish, EventType, Restaurant, User
from app.schemas import (
    AnalyticsEventCreate,
    CategoryOut,
    DishPublic,
    MenuPublic,
    OrderTrackPayload,
    RestaurantCreate,
    RestaurantOut,
    RestaurantPublic,
    RestaurantUpdate,
    StatsOut,
)

router = APIRouter(tags=["restaurants"])


@router.get("/restaurants", response_model=list[RestaurantOut])
async def list_restaurants(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Superadmin can see all restaurants; managers see only their own
    if user.email == "admin@menu.local":
        result = await db.execute(select(Restaurant).order_by(Restaurant.id))
    else:
        result = await db.execute(select(Restaurant).where(Restaurant.owner_id == user.id).order_by(Restaurant.id))
    return result.scalars().all()


@router.post("/restaurants", response_model=RestaurantOut)
async def create_restaurant(
    data: RestaurantCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Only superadmin (admin@menu.local) can create restaurants
    if user.email != "admin@menu.local":
        raise HTTPException(status_code=403, detail="Only superadmin can create restaurants")

    # Check if manager email already registered
    existing_user = await db.execute(select(User).where(User.email == data.manager_email))
    manager_user = existing_user.scalar_one_or_none()
    if manager_user:
        raise HTTPException(status_code=400, detail="Manager email already registered")

    # Create new user for the manager
    manager_user = User(email=data.manager_email, hashed_password=hash_password(data.manager_password))
    db.add(manager_user)
    await db.flush() # Flush to get manager_user.id

    slug = generate_slug(data.name)
    base_slug = slug
    counter = 1
    while True:
        existing = await db.execute(select(Restaurant).where(Restaurant.slug == slug))
        if not existing.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    short_code = generate_short_code()
    while True:
        existing = await db.execute(select(Restaurant).where(Restaurant.short_code == short_code))
        if not existing.scalar_one_or_none():
            break
        short_code = generate_short_code()

    restaurant = Restaurant(
        owner_id=manager_user.id,
        name=data.name,
        slug=slug,
        short_code=short_code,
        description=data.description,
        telegram_username=data.telegram_username,
        whatsapp_phone=data.whatsapp_phone,
        currency=data.currency,
    )
    db.add(restaurant)
    await db.commit()
    await db.refresh(restaurant)

    default_categories = [
        ("Хиты", "hits", 0),
        ("Завтраки", "breakfast", 1),
        ("Салаты", "salads", 2),
        ("Горячие блюда", "hot", 3),
        ("Пицца", "pizza", 4),
        ("Бургеры", "burgers", 5),
        ("Напитки", "drinks", 6),
        ("Десерты", "desserts", 7),
    ]
    for name, cat_slug, order in default_categories:
        db.add(Category(restaurant_id=restaurant.id, name=name, slug=cat_slug, sort_order=order))

    await db.commit()
    return restaurant


@router.get("/restaurants/managers", response_model=list[dict])
async def list_restaurant_managers(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all restaurants with their manager emails. Superadmin only."""
    if user.email != "admin@menu.local":
        raise HTTPException(status_code=403, detail="Superadmin only")

    result = await db.execute(
        select(Restaurant, User)
        .join(User, Restaurant.owner_id == User.id)
        .order_by(Restaurant.id)
    )
    rows = result.all()
    return [
        {
            "restaurant_id": r.id,
            "restaurant_name": r.name,
            "restaurant_slug": r.slug,
            "manager_email": u.email,
            "is_active": r.is_active,
        }
        for r, u in rows
    ]


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantOut)
async def get_restaurant(restaurant: Restaurant = Depends(get_restaurant_for_owner)):
    return restaurant


@router.patch("/restaurants/{restaurant_id}", response_model=RestaurantOut)
async def update_restaurant(
    data: RestaurantUpdate,
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(restaurant, field, value)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


@router.delete("/restaurants/{restaurant_id}")
async def delete_restaurant(
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    await db.delete(restaurant)
    await db.commit()
    return {"ok": True}


@router.get("/menu/{slug}", response_model=MenuPublic)
async def get_public_menu(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Restaurant).where(Restaurant.slug == slug, Restaurant.is_active == True))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Menu not found")

    db.add(AnalyticsEvent(restaurant_id=restaurant.id, event_type=EventType.MENU_VIEW.value))
    await db.commit()

    cats_result = await db.execute(
        select(Category)
        .where(Category.restaurant_id == restaurant.id, Category.is_active == True)
        .order_by(Category.sort_order)
    )
    categories = cats_result.scalars().all()

    dishes_result = await db.execute(
        select(Dish, Category)
        .join(Category, Dish.category_id == Category.id)
        .where(Dish.restaurant_id == restaurant.id, Dish.is_hidden == False)
        .order_by(Dish.sort_order, Dish.id)
    )
    rows = dishes_result.all()

    dishes_public = []
    for dish, cat in rows:
        images = json.loads(dish.images) if dish.images else []
        dishes_public.append(
            DishPublic(
                id=dish.id,
                name=dish.name,
                description=dish.description,
                price=dish.price,
                images=images,
                is_hit=dish.is_hit,
                category_id=cat.id,
                category_slug=cat.slug,
                category_name=cat.name,
            )
        )

    return MenuPublic(
        restaurant=RestaurantPublic.model_validate(restaurant),
        categories=[CategoryOut.model_validate(c) for c in categories],
        dishes=dishes_public,
    )


@router.get("/resolve/{short_code}")
async def resolve_short_code(short_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Restaurant).where(Restaurant.short_code == short_code, Restaurant.is_active == True)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Menu not found")
    return {"slug": restaurant.slug}


@router.get("/m/{short_code}", response_model=MenuPublic)
async def get_menu_by_short_code(short_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Restaurant).where(Restaurant.short_code == short_code, Restaurant.is_active == True)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Menu not found")
    return await get_public_menu(restaurant.slug, db)


@router.post("/menu/{slug}/analytics")
async def track_analytics(slug: str, data: AnalyticsEventCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Restaurant).where(Restaurant.slug == slug))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Menu not found")

    db.add(
        AnalyticsEvent(
            restaurant_id=restaurant.id,
            event_type=data.event_type,
            dish_id=data.dish_id,
            metadata_json=json.dumps(data.metadata) if data.metadata else None,
        )
    )
    await db.commit()
    return {"ok": True}


@router.post("/menu/{slug}/order")
async def track_order(slug: str, data: OrderTrackPayload, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Restaurant).where(Restaurant.slug == slug))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Menu not found")

    event_type = (
        EventType.TELEGRAM_CLICK.value if data.messenger == "telegram" else EventType.WHATSAPP_CLICK.value
    )
    db.add(AnalyticsEvent(restaurant_id=restaurant.id, event_type=event_type))
    db.add(AnalyticsEvent(restaurant_id=restaurant.id, event_type=EventType.ORDER_STARTED.value))

    for item in data.items:
        dish_result = await db.execute(select(Dish).where(Dish.id == item.dish_id))
        dish = dish_result.scalar_one_or_none()
        if dish:
            dish.order_count += item.quantity

    await db.commit()
    return {"ok": True}


@router.get("/restaurants/{restaurant_id}/stats", response_model=StatsOut)
async def get_stats(
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    db: AsyncSession = Depends(get_db),
):
    async def count_event(event_type: str) -> int:
        result = await db.execute(
            select(func.count())
            .select_from(AnalyticsEvent)
            .where(AnalyticsEvent.restaurant_id == restaurant.id, AnalyticsEvent.event_type == event_type)
        )
        return result.scalar() or 0

    dishes_result = await db.execute(
        select(Dish).where(Dish.restaurant_id == restaurant.id).order_by(Dish.order_count.desc()).limit(10)
    )
    popular = [
        {"id": d.id, "name": d.name, "order_count": d.order_count, "price": d.price}
        for d in dishes_result.scalars().all()
        if d.order_count > 0
    ]

    return StatsOut(
        menu_views=await count_event(EventType.MENU_VIEW.value),
        orders_count=await count_event(EventType.ORDER_STARTED.value),
        telegram_clicks=await count_event(EventType.TELEGRAM_CLICK.value),
        whatsapp_clicks=await count_event(EventType.WHATSAPP_CLICK.value),
        popular_dishes=popular,
    )


@router.get("/restaurants/{restaurant_id}/qr")
async def get_qr_code(
    restaurant: Restaurant = Depends(get_restaurant_for_owner),
    base_url: str = Query("http://localhost:5173"),
):
    menu_url = f"{base_url.rstrip('/')}/menu/{restaurant.slug}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(menu_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
