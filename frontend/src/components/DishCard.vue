<script setup lang="ts">
import { formatPrice, imageUrl } from '@/composables/useOrder'
import type { Dish } from '@/types'

defineProps<{ dish: Dish; currency: string }>()
defineEmits<{ add: [dish: Dish] }>()
</script>

<template>
  <article class="card">
    <div class="card__image-wrap">
      <img
        :src="imageUrl(dish.images[0] || '')"
        :alt="dish.name"
        class="card__image"
        loading="lazy"
      />
      <span v-if="dish.is_hit" class="card__badge">Хит</span>
      <div class="card__overlay">
        <button class="card__add-btn" @click="$emit('add', dish)">
          Добавить
        </button>
      </div>
    </div>
    <div class="card__body">
      <h3 class="card__name">{{ dish.name }}</h3>
      <p v-if="dish.description" class="card__desc">{{ dish.description }}</p>
      <div class="card__footer">
        <span class="card__price">{{ formatPrice(dish.price, currency) }}</span>
        <button class="card__add-mobile" aria-label="Добавить" @click="$emit('add', dish)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 5v14M5 12h14"/>
          </svg>
        </button>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
}

.card__image-wrap {
  position: relative;
  aspect-ratio: 4/5;
  overflow: hidden;
  background: var(--color-bg-secondary);
}

.card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover .card__image {
  transform: scale(1.04);
}

.card__badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  background: var(--color-text);
  color: var(--color-bg);
  font-size: 10px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.card__overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 24px;
  background: linear-gradient(transparent 50%, rgba(0,0,0,0.3));
  opacity: 0;
  transition: opacity var(--transition-smooth);
}

.card:hover .card__overlay { opacity: 1; }

.card__add-btn {
  padding: 12px 32px;
  background: var(--color-bg);
  color: var(--color-text);
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  transform: translateY(8px);
  transition: transform var(--transition-fast);
}

.card:hover .card__add-btn { transform: translateY(0); }

.card__body {
  padding: var(--spacing-sm) 0;
}

.card__name {
  font-size: 1.1rem;
  font-weight: 400;
  margin-bottom: 4px;
}

.card__desc {
  font-size: 12px;
  color: var(--color-text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--spacing-xs);
}

.card__price {
  font-size: 13px;
  letter-spacing: 0.04em;
}

.card__add-mobile {
  display: none;
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .card__overlay { display: none; }
  .card__add-mobile { display: flex; }
}
</style>
