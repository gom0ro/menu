<script setup lang="ts">
import { formatPrice } from '@/composables/useOrder'
import { useCartStore } from '@/stores/cart'
import { storeToRefs } from 'pinia'

defineProps<{ currency: string }>()
const emit = defineEmits<{ checkout: []; close: [] }>()

const cart = useCartStore()
const { items, totalPrice, isOpen } = storeToRefs(cart)
</script>

<template>
  <Teleport to="body">
    <transition name="fade">
      <div v-if="isOpen" class="cart-backdrop" @click="emit('close')" />
    </transition>
    <transition name="slide-right">
      <aside v-if="isOpen" class="cart" role="dialog" aria-label="Корзина">
        <div class="cart__header">
          <h2 class="cart__title">Корзина</h2>
          <button class="cart__close" aria-label="Закрыть" @click="emit('close')">✕</button>
        </div>

        <div v-if="items.length === 0" class="cart__empty">
          <p>Корзина пуста</p>
          <span>Выберите блюда из меню</span>
        </div>

        <ul v-else class="cart__list">
          <li v-for="item in items" :key="item.dish.id" class="cart__item">
            <div class="cart__item-info">
              <span class="cart__item-name">{{ item.dish.name }}</span>
              <span class="cart__item-price">{{ formatPrice(item.dish.price * item.quantity, currency) }}</span>
            </div>
            <div class="cart__qty">
              <button @click="cart.setQuantity(item.dish.id, item.quantity - 1)">−</button>
              <span>{{ item.quantity }}</span>
              <button @click="cart.setQuantity(item.dish.id, item.quantity + 1)">+</button>
            </div>
          </li>
        </ul>

        <div v-if="items.length > 0" class="cart__footer">
          <div class="cart__total">
            <span>Итого</span>
            <span>{{ formatPrice(totalPrice, currency) }}</span>
          </div>
          <button class="cart__checkout" @click="emit('checkout')">
            Оформить заказ
          </button>
        </div>
      </aside>
    </transition>
  </Teleport>
</template>

<style scoped>
.cart-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 200;
  backdrop-filter: blur(2px);
}

.cart {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(420px, 100vw);
  background: var(--color-bg);
  border-left: 1px solid var(--color-border);
  z-index: 201;
  display: flex;
  flex-direction: column;
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.08);
}

.cart__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.cart__title {
  font-size: 1.25rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.cart__close {
  font-size: 18px;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
}

.cart__close:hover { color: var(--color-text); }

.cart__empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--color-text-muted);
}

.cart__list {
  flex: 1;
  overflow-y: auto;
  list-style: none;
  padding: var(--spacing-md) var(--spacing-lg);
}

.cart__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border);
  gap: var(--spacing-sm);
}

.cart__item-name {
  font-size: 13px;
  display: block;
}

.cart__item-price {
  font-size: 12px;
  color: var(--color-text-muted);
}

.cart__qty {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.cart__qty button {
  width: 28px;
  height: 28px;
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all var(--transition-fast);
}

.cart__qty button:hover {
  background: var(--color-text);
  color: var(--color-bg);
  border-color: var(--color-text);
}

.cart__footer {
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.cart__total {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: var(--spacing-md);
}

.cart__checkout {
  width: 100%;
  padding: 16px;
  background: var(--color-text);
  color: var(--color-bg);
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  transition: opacity var(--transition-fast);
}

.cart__checkout:hover { opacity: 0.85; }
</style>
