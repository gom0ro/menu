import asyncio
import traceback
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Restaurant, Category, Dish, AnalyticsEvent, EventType
import json

async def main():
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            # 1. Query restaurant
            result = await db.execute(select(Restaurant).where(Restaurant.slug == "la-maison", Restaurant.is_active == True))
            restaurant = result.scalar_one_or_none()
            print("Restaurant found:", restaurant.name if restaurant else None)
            if not restaurant:
                return

            # 2. Add analytics event (this is what get_public_menu does!)
            event = AnalyticsEvent(restaurant_id=restaurant.id, event_type=EventType.MENU_VIEW.value)
            db.add(event)
            await db.commit()
            print("Analytics event added!")

            # 3. Query categories
            cats_result = await db.execute(
                select(Category)
                .where(Category.restaurant_id == restaurant.id, Category.is_active == True)
                .order_by(Category.sort_order)
            )
            categories = cats_result.scalars().all()
            print("Categories count:", len(categories))

            # 4. Query dishes
            dishes_result = await db.execute(
                select(Dish, Category)
                .join(Category, Dish.category_id == Category.id)
                .where(Dish.restaurant_id == restaurant.id, Dish.is_hidden == False)
                .order_by(Dish.sort_order, Dish.id)
            )
            rows = dishes_result.all()
            print("Dishes count:", len(rows))
            
        except Exception as e:
            print("FAILED AT DB level:")
            traceback.print_exc()
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
