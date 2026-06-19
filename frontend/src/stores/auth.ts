import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const { access_token } = await api.login(email, password)
      localStorage.setItem('token', access_token)
      user.value = await api.me()
    } finally {
      loading.value = false
    }
  }

  async function checkAuth() {
    const token = localStorage.getItem('token')
    if (!token) return false
    try {
      user.value = await api.me()
      return true
    } catch {
      localStorage.removeItem('token')
      return false
    }
  }

  function logout() {
    localStorage.removeItem('token')
    user.value = null
  }

  return { user, loading, login, checkAuth, logout }
})
