<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const email = ref('admin@menu.local')
const password = ref('admin123')
const error = ref('')

const SUPERADMIN_EMAIL = 'admin@menu.local'

async function submit() {
  error.value = ''
  try {
    await auth.login(email.value, password.value)

    // Superadmin goes to the global dashboard
    if (auth.user?.email === SUPERADMIN_EMAIL) {
      const redirect = (route.query.redirect as string) || '/admin/dashboard'
      router.push(redirect)
      return
    }

    // Manager: find their restaurant and redirect to its panel
    try {
      const { api } = await import('@/api/client')
      const restaurants = await api.getRestaurants()
      if (restaurants.length > 0) {
        router.push(`/menu/${restaurants[0].slug}/admin`)
        return
      }
    } catch {
      // fallback
    }

    // Fallback for manager with no restaurant yet
    router.push('/admin/dashboard')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка входа'
  }
}
</script>

<template>
  <div class="login">
    <form class="login__card" @submit.prevent="submit">
      <h1 class="login__title">Админ-панель</h1>
      <p class="login__subtitle">Электронное меню</p>

      <label>
        <span>Email</span>
        <input v-model="email" type="email" required />
      </label>
      <label>
        <span>Пароль</span>
        <input v-model="password" type="password" required />
      </label>

      <p v-if="error" class="login__error">{{ error }}</p>

      <button type="submit" class="login__btn" :disabled="auth.loading">
        {{ auth.loading ? 'Вход...' : 'Войти' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md);
}

.login__card {
  width: min(400px, 100%);
  padding: var(--spacing-xl);
  border: 1px solid var(--color-border);
}

.login__title {
  font-size: 1.75rem;
  text-align: center;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.login__subtitle {
  text-align: center;
  color: var(--color-text-muted);
  font-size: 12px;
  margin: 8px 0 var(--spacing-lg);
  letter-spacing: 0.1em;
}

.login__card label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.login__card label span {
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.login__card input {
  padding: 12px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text);
}

.login__error {
  color: #c44;
  font-size: 13px;
  margin-bottom: 12px;
}

.login__btn {
  width: 100%;
  padding: 14px;
  background: var(--color-text);
  color: var(--color-bg);
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-top: 8px;
}

.login__btn:disabled { opacity: 0.6; }
</style>
