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
}

export interface MenuData {
  restaurant: Restaurant
  categories: Category[]
  dishes: Dish[]
}

export interface CartItem {
  dish: Dish
  quantity: number
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
