<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/api/client'
import type { Restaurant } from '@/types'

const restaurants = ref<Restaurant[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    restaurants.value = await api.getRestaurants()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="dashboard">
    <h1>Обзор</h1>
    <p class="dashboard__desc">Управление электронными меню ресторанов</p>

    <div v-if="loading" class="dashboard__loading">Загрузка...</div>

    <div v-else class="dashboard__grid">
      <div v-for="r in restaurants" :key="r.id" class="dashboard__card">
        <h3>{{ r.name }}</h3>
        <p>{{ r.description || 'Без описания' }}</p>
        <div class="dashboard__links">
          <a :href="`/menu/${r.slug}`" target="_blank" class="dashboard__link">Открыть меню →</a>
          <span class="dashboard__code">/{{ r.slug }}</span>
        </div>
      </div>
      <router-link to="/admin/restaurants" class="dashboard__card dashboard__card--add">
        + Добавить ресторан
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.dashboard h1 {
  font-size: 2rem;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}

.dashboard__desc {
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-lg);
}

.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
}

.dashboard__card {
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border);
  transition: border-color var(--transition-fast);
}

.dashboard__card:hover { border-color: var(--color-text); }

.dashboard__card h3 {
  font-size: 1.25rem;
  margin-bottom: 8px;
}

.dashboard__card p {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-md);
}

.dashboard__links {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dashboard__link {
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.dashboard__code {
  font-size: 11px;
  color: var(--color-text-muted);
  font-family: monospace;
}

.dashboard__card--add {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  font-size: 13px;
  letter-spacing: 0.06em;
  min-height: 160px;
}
</style>
