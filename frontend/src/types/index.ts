export interface Restaurant {
  id: number
  name: string
  slug: string
  description: string | null
  logo_url: string | null
  telegram_username: string | null
  whatsapp_phone: string | null
  currency: string
  short_code?: string
  is_active?: boolean
}

export interface Category {
  id: number
  name: string
  slug: string
  sort_order: number
  is_active: boolean
  restaurant_id?: number
}

export interface ModifierOption {
  id: number
  group_id: number
  name: string
  price_delta: number
}

export interface ModifierGroup {
  id: number
  dish_id: number
  name: string
  is_required: boolean
  max_choices: number
  options: ModifierOption[]
}

export interface Dish {
  id: number
  name: string
  description: string | null
  price: number
  images: string[]
  is_hit: boolean
  category_id: number
  category_slug: string
  category_name: string
  is_hidden?: boolean
  sort_order?: number
  order_count?: number
  restaurant_id?: number
  modifier_groups?: ModifierGroup[]
}

export interface MenuData {
  restaurant: Restaurant
  categories: Category[]
  dishes: Dish[]
}

export interface CartItem {
  cartItemId: string
  dish: Dish
  quantity: number
  price: number
  modifiers?: { id: number; name: string; price_delta: number; group_name: string }[]
}

export interface Stats {
  menu_views: number
  orders_count: number
  telegram_clicks: number
  whatsapp_clicks: number
  popular_dishes: { id: number; name: string; order_count: number; price: number }[]
}

export interface User {
  id: number
  email: string
}
