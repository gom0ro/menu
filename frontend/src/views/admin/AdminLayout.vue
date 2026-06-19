<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/admin/login')
}

const links = [
  { to: '/admin/dashboard', label: 'Обзор' },
  { to: '/admin/restaurants', label: 'Рестораны' },
  { to: '/admin/dishes', label: 'Блюда' },
  { to: '/admin/categories', label: 'Категории' },
  { to: '/admin/stats', label: 'Статистика' },
]
</script>

<template>
  <div class="admin">
    <aside class="admin__sidebar">
      <div class="admin__brand">Menu Admin</div>
      <nav class="admin__nav">
        <router-link
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="admin__link"
          active-class="admin__link--active"
        >
          {{ link.label }}
        </router-link>
      </nav>
      <button class="admin__logout" @click="logout">Выйти</button>
    </aside>
    <main class="admin__main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin {
  display: flex;
  min-height: 100vh;
}

.admin__sidebar {
  width: 240px;
  border-right: 1px solid var(--color-border);
  padding: var(--spacing-lg) var(--spacing-md);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
}

.admin__brand {
  font-family: var(--font-display);
  font-size: 1.25rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: var(--spacing-lg);
}

.admin__nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.admin__link {
  padding: 10px 12px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}

.admin__link:hover,
.admin__link--active {
  color: var(--color-text);
  background: var(--color-hover);
}

.admin__logout {
  padding: 10px;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  border-top: 1px solid var(--color-border);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
}

.admin__main {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
}

@media (max-width: 768px) {
  .admin { flex-direction: column; }
  .admin__sidebar {
    width: 100%;
    height: auto;
    position: relative;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }
  .admin__nav { flex-direction: row; flex-wrap: wrap; flex: none; }
  .admin__logout { border: none; margin: 0; padding: 10px 12px; }
}
</style>
