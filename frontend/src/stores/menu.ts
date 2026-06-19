import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'
import type { MenuData } from '@/types'

export const useMenuStore = defineStore('menu', () => {
  const data = ref<MenuData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMenu(slug: string) {
    loading.value = true
    error.value = null
    try {
      data.value = await api.getMenu(slug)
      document.title = `${data.value.restaurant.name} — Меню`
      const meta = document.querySelector('meta[name="description"]')
      if (meta && data.value.restaurant.description) {
        meta.setAttribute('content', data.value.restaurant.description)
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Не удалось загрузить меню'
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, fetchMenu }
})
