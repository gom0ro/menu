<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import MenuHeader from '@/components/MenuHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import CategoryFilter from '@/components/CategoryFilter.vue'
import DishCard from '@/components/DishCard.vue'
import DishSkeleton from '@/components/DishSkeleton.vue'
import CartSidebar from '@/components/CartSidebar.vue'
import OrderModal from '@/components/OrderModal.vue'
import { useMenuStore } from '@/stores/menu'
import { useCartStore } from '@/stores/cart'
import { useThemeStore } from '@/stores/theme'
import type { Dish } from '@/types'

const route = useRoute()
const menuStore = useMenuStore()
const cart = useCartStore()
const theme = useThemeStore()

const { data, loading, error } = storeToRefs(menuStore)
const { totalItems, totalPrice, items } = storeToRefs(cart)
const { isDark } = storeToRefs(theme)

const search = ref('')
const activeCategory = ref('all')
const orderOpen = ref(false)

const slug = computed(() => route.params.slug as string)

const filteredDishes = computed(() => {
  if (!data.value) return []
  let dishes = data.value.dishes

  if (activeCategory.value === 'hits') {
    dishes = dishes.filter((d) => d.is_hit)
  } else if (activeCategory.value !== 'all') {
    dishes = dishes.filter((d) => d.category_slug === activeCategory.value)
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    dishes = dishes.filter(
      (d) =>
        d.name.toLowerCase().includes(q) ||
        d.description?.toLowerCase().includes(q),
    )
  }

  return dishes
})

const groupedDishes = computed(() => {
  if (!data.value || activeCategory.value !== 'all' || search.value.trim()) {
    return [{ name: '', dishes: filteredDishes.value }]
  }

  const groups: { name: string; dishes: Dish[] }[] = []
  for (const cat of data.value.categories) {
    const catDishes = filteredDishes.value.filter((d) => d.category_slug === cat.slug)
    if (catDishes.length > 0) {
      groups.push({ name: cat.name, dishes: catDishes })
    }
  }
  return groups
})

function onAdd(dish: Dish) {
  cart.add(dish)
  cart.open()
}

function onCheckout() {
  cart.close()
  orderOpen.value = true
}

onMounted(() => menuStore.fetchMenu(slug.value))
watch(slug, (s) => menuStore.fetchMenu(s))
</script>

<template>
  <div class="menu-page">
    <template v-if="loading">
      <div class="menu-page__container">
        <div class="skeleton skeleton--header" />
        <DishSkeleton />
      </div>
    </template>

    <template v-else-if="error">
      <div class="menu-page__error">
        <h2>Меню не найдено</h2>
        <p>{{ error }}</p>
      </div>
    </template>

    <template v-else-if="data">
      <MenuHeader
        :restaurant-name="data.restaurant.name"
        :description="data.restaurant.description"
        :cart-count="totalItems"
        :is-dark="isDark"
        @open-cart="cart.open()"
        @toggle-theme="theme.toggle()"
      />

      <main class="menu-page__container">
        <div class="menu-page__toolbar">
          <SearchBar v-model="search" />
        </div>

        <CategoryFilter
          :categories="data.categories"
          :active="activeCategory"
          @select="activeCategory = $event"
        />

        <section
          v-for="group in groupedDishes"
          :key="group.name || 'all'"
          class="menu-section"
        >
          <h2 v-if="group.name" class="menu-section__title">{{ group.name }}</h2>
          <div class="menu-grid">
            <DishCard
              v-for="dish in group.dishes"
              :key="dish.id"
              :dish="dish"
              :currency="data.restaurant.currency"
              @add="onAdd"
            />
          </div>
        </section>

        <p v-if="filteredDishes.length === 0" class="menu-page__empty">
          Блюда не найдены
        </p>
      </main>

      <CartSidebar
        :currency="data.restaurant.currency"
        @close="cart.close()"
        @checkout="onCheckout"
      />

      <OrderModal
        :open="orderOpen"
        :items="items"
        :total="totalPrice"
        :currency="data.restaurant.currency"
        :slug="slug"
        :telegram="data.restaurant.telegram_username"
        :whatsapp="data.restaurant.whatsapp_phone"
        @close="orderOpen = false"
        @success="cart.clear()"
      />
    </template>
  </div>
</template>

<style scoped>
.menu-page {
  min-height: 100vh;
}

.menu-page__container {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.menu-page__toolbar {
  margin-bottom: var(--spacing-md);
}

.menu-section {
  margin-top: var(--spacing-xl);
}

.menu-section__title {
  font-size: clamp(1.25rem, 2.5vw, 1.75rem);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--spacing-lg);
}

.menu-page__empty {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--spacing-xl);
}

.menu-page__error {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.skeleton--header {
  height: 80px;
  margin-bottom: var(--spacing-lg);
}

@media (max-width: 768px) {
  .menu-page__container { padding: var(--spacing-md); }
  .menu-grid { gap: var(--spacing-md); grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 480px) {
  .menu-grid { grid-template-columns: 1fr; }
}
</style>
