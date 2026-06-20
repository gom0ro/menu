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
  { to: '/admin/stats', label: 'Логины' },
]
</script>

<template>
  <div class="admin">
    <!-- Sleek Top Header for Mobile Screen -->
    <header class="admin__mobile-header">
      <span class="admin__brand">Menu Admin</span>
      <button class="admin__logout-btn" @click="logout" aria-label="Выйти">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </header>

    <!-- Sidebar for Desktop Screen -->
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

    <!-- Main Content Area -->
    <main class="admin__main">
      <router-view />
    </main>

    <!-- Bottom Tab Navigation Bar for Mobile Screen -->
    <nav class="admin__bottom-nav">
      <router-link
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        class="admin__tab-link"
        active-class="admin__tab-link--active"
      >
        <span class="admin__tab-icon">
          <!-- Overview Tab -->
          <svg v-if="link.label === 'Обзор'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="9"/>
            <rect x="14" y="3" width="7" height="5"/>
            <rect x="14" y="12" width="7" height="9"/>
            <rect x="3" y="16" width="7" height="5"/>
          </svg>
          <!-- Restaurants Tab -->
          <svg v-else-if="link.label === 'Рестораны'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <!-- Dishes Tab -->
          <svg v-else-if="link.label === 'Блюда'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="5" r="3"/>
            <line x1="12" y1="22" x2="12" y2="8"/>
            <path d="M5 12H2a10 10 0 0 0 20 0h-3"/>
          </svg>
          <!-- Categories Tab -->
          <svg v-else-if="link.label === 'Категории'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="4" y1="9" x2="20" y2="9"/>
            <line x1="4" y1="15" x2="20" y2="15"/>
            <line x1="10" y1="3" x2="8" y2="21"/>
            <line x1="16" y1="3" x2="14" y2="21"/>
          </svg>
          <!-- Stats/Logins Tab -->
          <svg v-else-if="link.label === 'Логины'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
          </svg>
        </span>
        <span class="admin__tab-label">{{ link.label }}</span>
      </router-link>
    </nav>
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
  padding: 12px 16px;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
  border-radius: var(--radius-sm);
}

.admin__link:hover,
.admin__link--active {
  color: var(--color-text);
  background: var(--color-hover);
}

.admin__logout {
  padding: 12px;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  border-top: 1px solid var(--color-border);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  text-align: left;
}

.admin__logout:hover {
  color: var(--color-text);
}

.admin__main {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
  background: var(--color-bg-secondary);
}

/* Mobile styles default hidden */
.admin__mobile-header {
  display: none;
}

.admin__bottom-nav {
  display: none;
}

@media (max-width: 768px) {
  .admin {
    flex-direction: column;
  }

  .admin__sidebar {
    display: none;
  }

  .admin__mobile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    padding: 0 var(--spacing-md);
    background: var(--color-bg);
    border-bottom: 1px solid var(--color-border);
    position: sticky;
    top: 0;
    z-index: 90;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }

  .admin__mobile-header .admin__brand {
    margin-bottom: 0;
    font-size: 1rem;
    letter-spacing: 0.08em;
  }

  .admin__logout-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    color: var(--color-text-muted);
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
  }

  .admin__logout-btn:hover {
    background: var(--color-hover);
    color: var(--color-text);
  }

  .admin__main {
    padding: var(--spacing-md);
    padding-bottom: calc(64px + var(--spacing-md) + env(safe-area-inset-bottom, 0px));
  }

  .admin__bottom-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: calc(60px + env(safe-area-inset-bottom, 0px));
    background: var(--color-bg);
    border-top: 1px solid var(--color-border);
    z-index: 90;
    padding-bottom: env(safe-area-inset-bottom, 0px);
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.03);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }

  .admin__tab-link {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--color-text-muted);
    gap: 4px;
    transition: all var(--transition-fast);
  }

  .admin__tab-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 20px;
  }

  .admin__tab-label {
    font-size: 8px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 400;
  }

  .admin__tab-link:hover {
    color: var(--color-text);
  }

  .admin__tab-link--active {
    color: var(--color-text);
  }
}
</style>
