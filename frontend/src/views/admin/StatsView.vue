<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { formatPrice } from '@/composables/useOrder'
import type { Restaurant, Stats } from '@/types'

const restaurants = ref<Restaurant[]>([])
const selectedId = ref<number | null>(null)
const stats = ref<Stats | null>(null)
const loading = ref(true)

async function load() {
  restaurants.value = await api.getRestaurants()
  if (restaurants.value.length && !selectedId.value) {
    selectedId.value = restaurants.value[0].id
  }
  await loadStats()
  loading.value = false
}

async function loadStats() {
  if (!selectedId.value) return
  stats.value = await api.getStats(selectedId.value)
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page__header">
      <h1>Статистика</h1>
      <select v-model="selectedId" @change="loadStats">
        <option v-for="r in restaurants" :key="r.id" :value="r.id">{{ r.name }}</option>
      </select>
    </div>

    <div v-if="loading">Загрузка...</div>

    <template v-else-if="stats">
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-card__value">{{ stats.menu_views }}</span>
          <span class="stat-card__label">Открытий меню</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__value">{{ stats.orders_count }}</span>
          <span class="stat-card__label">Заказов</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__value">{{ stats.telegram_clicks }}</span>
          <span class="stat-card__label">Переходов в Telegram</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__value">{{ stats.whatsapp_clicks }}</span>
          <span class="stat-card__label">Переходов в WhatsApp</span>
        </div>
      </div>

      <section v-if="stats.popular_dishes.length" class="popular">
        <h2>Популярные блюда</h2>
        <div class="popular__list">
          <div v-for="(d, i) in stats.popular_dishes" :key="d.id" class="popular__item">
            <span class="popular__rank">{{ i + 1 }}</span>
            <span class="popular__name">{{ d.name }}</span>
            <span class="popular__count">{{ d.order_count }} заказов</span>
            <span class="popular__price">{{ formatPrice(d.price) }}</span>
          </div>
        </div>
      </section>
      <p v-else class="empty">Пока нет данных о популярных блюдах</p>
    </template>
  </div>
</template>

<style scoped>
.page__header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--spacing-lg);
}
.page h1 { font-size: 1.75rem; }
select {
  padding: 8px 12px; border: 1px solid var(--color-border);
  background: transparent; color: var(--color-text);
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}
.stat-card {
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.stat-card__value {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 300;
}
.stat-card__label {
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}
.popular h2 {
  font-size: 1.25rem;
  margin-bottom: var(--spacing-md);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.popular__item {
  display: grid;
  grid-template-columns: 40px 1fr auto auto;
  gap: 16px;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 13px;
}
.popular__rank {
  font-family: var(--font-display);
  font-size: 1.25rem;
  color: var(--color-text-muted);
}
.popular__count { color: var(--color-text-muted); font-size: 12px; }
.empty { color: var(--color-text-muted); }
</style>
