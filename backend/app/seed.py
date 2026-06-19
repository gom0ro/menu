import json

from sqlalchemy import select

from app.auth import generate_short_code, generate_slug, hash_password
from app.database import async_session
from app.models import Category, Dish, Restaurant, User

DEMO_DISHES = [
    ("Пицца Маргарита", "Томатный соус, моцарелла, базилик", 4500, "pizza", True),
    ("Пицца Пепперони", "Острая салями, моцарелла, томатный соус", 5200, "pizza", True),
    ("Цезарь", "Курица, пармезан, романо, соус цезарь", 3200, "salads", True),
    ("Греческий салат", "Фета, оливки, огурцы, помидоры", 2800, "salads", False),
    ("Бургер Классик", "Говяжья котлета, сыр, салат, соус", 3800, "burgers", True),
    ("Двойной бургер", "Две котлеты, чеддер, бекон", 4800, "burgers", False),
    ("Яичница с беконом", "3 яйца, хрустящий бекон, тост", 2200, "breakfast", False),
    ("Круассан", "Свежая выпечка с маслом", 1500, "breakfast", False),
    ("Стейк Рибай", "300г, соус перечный", 8900, "hot", True),
    ("Паста Карбонара", "Спагетти, бекон, пармезан", 4200, "hot", False),
    ("Кола", "0.5л", 800, "drinks", False),
    ("Лимонад", "Домашний, мята", 1200, "drinks", False),
    ("Тирамису", "Классический итальянский десерт", 2500, "desserts", True),
    ("Чизкейк", "Нью-Йорк стиль", 2800, "desserts", False),
]

PLACEHOLDER_IMAGES = {
    "pizza": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800&q=80",
    "salads": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=800&q=80",
    "burgers": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=80",
    "breakfast": "https://images.unsplash.com/photo-1533089860892-a7c6f948aeee?w=800&q=80",
    "hot": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&q=80",
    "drinks": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=800&q=80",
    "desserts": "https://images.unsplash.com/photo-1551024506-0bccd28d11ad?w=800&q=80",
}


async def seed_demo_data():
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == "admin@menu.local"))
        if result.scalar_one_or_none():
            return

        user = User(email="admin@menu.local", hashed_password=hash_password("admin123"))
        db.add(user)
        await db.flush()

        restaurant = Restaurant(
            owner_id=user.id,
            name="La Maison",
            slug="la-maison",
            short_code=generate_short_code(),
            description="Премиальная кухня в центре города",
            telegram_username="restaurant_owner",
            whatsapp_phone="77001234567",
            currency="₸",
        )
        db.add(restaurant)
        await db.flush()

        categories_data = [
            ("Хиты", "hits", 0),
            ("Завтраки", "breakfast", 1),
            ("Салаты", "salads", 2),
            ("Горячие блюда", "hot", 3),
            ("Пицца", "pizza", 4),
            ("Бургеры", "burgers", 5),
            ("Напитки", "drinks", 6),
            ("Десерты", "desserts", 7),
        ]
        cat_map: dict[str, int] = {}
        for name, slug, order in categories_data:
            cat = Category(restaurant_id=restaurant.id, name=name, slug=slug, sort_order=order)
            db.add(cat)
            await db.flush()
            cat_map[slug] = cat.id

        for i, (name, desc, price, cat_slug, is_hit) in enumerate(DEMO_DISHES):
            db.add(
                Dish(
                    restaurant_id=restaurant.id,
                    category_id=cat_map[cat_slug],
                    name=name,
                    description=desc,
                    price=price,
                    images=json.dumps([PLACEHOLDER_IMAGES.get(cat_slug, PLACEHOLDER_IMAGES["hot"])]),
                    is_hit=is_hit,
                    sort_order=i,
                )
            )

        await db.commit()
