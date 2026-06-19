<script setup lang="ts">
import type { Category } from '@/types'

defineProps<{
  categories: Category[]
  active: string
}>()

defineEmits<{ select: [slug: string] }>()
</script>

<template>
  <nav class="filters" aria-label="Категории">
    <button
      class="filters__item"
      :class="{ 'filters__item--active': active === 'all' }"
      @click="$emit('select', 'all')"
    >
      Все
    </button>
    <button
      v-for="cat in categories"
      :key="cat.id"
      class="filters__item"
      :class="{ 'filters__item--active': active === cat.slug }"
      @click="$emit('select', cat.slug)"
    >
      {{ cat.name }}
    </button>
  </nav>
</template>

<style scoped>
.filters {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.filters::-webkit-scrollbar { display: none; }

.filters__item {
  flex-shrink: 0;
  padding: 8px 20px;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.filters__item:hover {
  border-color: var(--color-text);
  color: var(--color-text);
}

.filters__item--active {
  background: var(--color-text);
  color: var(--color-bg);
  border-color: var(--color-text);
}
</style>
