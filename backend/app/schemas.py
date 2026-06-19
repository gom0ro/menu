import json
from datetime import datetime

from pydantic import BaseModel, Field


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}


# Restaurant
class RestaurantBase(BaseModel):
    name: str
    description: str | None = None
    telegram_username: str | None = None
    whatsapp_phone: str | None = None
    currency: str = "₸"


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    telegram_username: str | None = None
    whatsapp_phone: str | None = None
    currency: str | None = None
    is_active: bool | None = None


class RestaurantOut(RestaurantBase):
    id: int
    slug: str
    short_code: str
    logo_url: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RestaurantPublic(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    telegram_username: str | None
    whatsapp_phone: str | None
    currency: str

    model_config = {"from_attributes": True}


# Category
class CategoryBase(BaseModel):
    name: str
    sort_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryOut(CategoryBase):
    id: int
    slug: str
    restaurant_id: int

    model_config = {"from_attributes": True}


# Dish
class DishBase(BaseModel):
    name: str
    description: str | None = None
    price: int = Field(gt=0)
    category_id: int
    is_hit: bool = False
    is_hidden: bool = False
    sort_order: int = 0


class DishCreate(DishBase):
    images: list[str] = []


class DishUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: int | None = Field(default=None, gt=0)
    category_id: int | None = None
    is_hit: bool | None = None
    is_hidden: bool | None = None
    sort_order: int | None = None
    images: list[str] | None = None


class DishOut(DishBase):
    id: int
    restaurant_id: int
    images: list[str]
    order_count: int

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_dish(cls, dish) -> "DishOut":
        images = json.loads(dish.images) if dish.images else []
        return cls(
            id=dish.id,
            restaurant_id=dish.restaurant_id,
            category_id=dish.category_id,
            name=dish.name,
            description=dish.description,
            price=dish.price,
            images=images,
            is_hit=dish.is_hit,
            is_hidden=dish.is_hidden,
            sort_order=dish.sort_order,
            order_count=dish.order_count,
        )


class DishPublic(BaseModel):
    id: int
    name: str
    description: str | None
    price: int
    images: list[str]
    is_hit: bool
    category_id: int
    category_slug: str
    category_name: str


# Analytics
class AnalyticsEventCreate(BaseModel):
    event_type: str
    dish_id: int | None = None
    metadata: dict | None = None


class OrderItemPayload(BaseModel):
    dish_id: int
    quantity: int = Field(gt=0)


class OrderTrackPayload(BaseModel):
    items: list[OrderItemPayload]
    messenger: str


class StatsOut(BaseModel):
    menu_views: int
    orders_count: int
    telegram_clicks: int
    whatsapp_clicks: int
    popular_dishes: list[dict]


class MenuPublic(BaseModel):
    restaurant: RestaurantPublic
    categories: list[CategoryOut]
    dishes: list[DishPublic]
