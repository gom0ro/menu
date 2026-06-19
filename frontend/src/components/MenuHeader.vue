<script setup lang="ts">
defineProps<{
  restaurantName: string
  description?: string | null
  cartCount: number
  isDark: boolean
}>()

defineEmits<{
  openCart: []
  toggleTheme: []
}>()
</script>

<template>
  <header class="header">
    <div class="header__inner">
      <div class="header__brand">
        <h1 class="header__title">{{ restaurantName }}</h1>
        <p v-if="description" class="header__desc">{{ description }}</p>
      </div>
      <div class="header__actions">
        <button class="header__icon-btn" aria-label="Тема" @click="$emit('toggleTheme')">
          <svg v-if="isDark" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>
        <button class="header__cart-btn" @click="$emit('openCart')">
          <span>Корзина</span>
          <transition name="fade">
            <span v-if="cartCount > 0" class="header__badge">{{ cartCount }}</span>
          </transition>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  backdrop-filter: blur(12px);
  transition: background var(--transition-smooth);
}

.header__inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.header__title {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 300;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.header__desc {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 4px;
  letter-spacing: 0.04em;
}

.header__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.header__icon-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  transition: all var(--transition-fast);
}

.header__icon-btn:hover {
  background: var(--color-hover);
}

.header__cart-btn {
  position: relative;
  padding: 10px 24px;
  border: 1px solid var(--color-text);
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  transition: all var(--transition-fast);
}

.header__cart-btn:hover {
  background: var(--color-text);
  color: var(--color-bg);
}

.header__badge {
  position: absolute;
  top: -8px;
  right: -8px;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: var(--color-text);
  color: var(--color-bg);
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

@media (max-width: 640px) {
  .header__inner { padding: var(--spacing-sm) var(--spacing-md); }
  .header__cart-btn span:first-child { display: none; }
  .header__cart-btn { padding: 10px 16px; }
  .header__cart-btn::before { content: '🛒'; }
}
</style>
