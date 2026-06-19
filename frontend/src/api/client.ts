const API_BASE = '/api'

function getToken(): string | null {
  return localStorage.getItem('token')
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
  ...(options.headers as Record<string, string>),
  }

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail || 'Request failed')
  }

  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<{ id: number; email: string }>('/auth/me'),

  getMenu: (slug: string) => request<import('@/types').MenuData>(`/menu/${slug}`),

  trackAnalytics: (slug: string, event_type: string, dish_id?: number) =>
    request('/menu/' + slug + '/analytics', {
      method: 'POST',
      body: JSON.stringify({ event_type, dish_id }),
    }),

  trackOrder: (slug: string, items: { dish_id: number; quantity: number }[], messenger: string) =>
    request('/menu/' + slug + '/order', {
      method: 'POST',
      body: JSON.stringify({ items, messenger }),
    }),

  getRestaurants: () => request<import('@/types').Restaurant[]>('/restaurants'),

  createRestaurant: (data: Partial<import('@/types').Restaurant>) =>
    request<import('@/types').Restaurant>('/restaurants', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateRestaurant: (id: number, data: Partial<import('@/types').Restaurant>) =>
    request<import('@/types').Restaurant>(`/restaurants/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteRestaurant: (id: number) =>
    request(`/restaurants/${id}`, { method: 'DELETE' }),

  getStats: (id: number) => request<import('@/types').Stats>(`/restaurants/${id}/stats`),

  getQrUrl: (id: number, baseUrl: string) =>
    `${API_BASE}/restaurants/${id}/qr?base_url=${encodeURIComponent(baseUrl)}`,

  getCategories: (restaurantId: number) =>
    request<import('@/types').Category[]>(`/restaurants/${restaurantId}/categories`),

  createCategory: (restaurantId: number, data: Partial<import('@/types').Category>) =>
    request<import('@/types').Category>(`/restaurants/${restaurantId}/categories`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateCategory: (restaurantId: number, id: number, data: Partial<import('@/types').Category>) =>
    request<import('@/types').Category>(`/restaurants/${restaurantId}/categories/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteCategory: (restaurantId: number, id: number) =>
    request(`/restaurants/${restaurantId}/categories/${id}`, { method: 'DELETE' }),

  getDishes: (restaurantId: number) =>
    request<import('@/types').Dish[]>(`/restaurants/${restaurantId}/dishes`),

  createDish: (restaurantId: number, data: Record<string, unknown>) =>
    request<import('@/types').Dish>(`/restaurants/${restaurantId}/dishes`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateDish: (restaurantId: number, id: number, data: Record<string, unknown>) =>
    request<import('@/types').Dish>(`/restaurants/${restaurantId}/dishes/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteDish: (restaurantId: number, id: number) =>
    request(`/restaurants/${restaurantId}/dishes/${id}`, { method: 'DELETE' }),

  uploadDishImage: async (restaurantId: number, dishId: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return request<import('@/types').Dish>(`/restaurants/${restaurantId}/dishes/${dishId}/images`, {
      method: 'POST',
      body: form,
      headers: {},
    })
  },
}
