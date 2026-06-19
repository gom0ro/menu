import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CartItem, Dish } from '@/types'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const isOpen = ref(false)

  const totalItems = computed(() => items.value.reduce((sum, i) => sum + i.quantity, 0))
  const totalPrice = computed(() => items.value.reduce((sum, i) => sum + i.dish.price * i.quantity, 0))

  function add(dish: Dish) {
    const existing = items.value.find((i) => i.dish.id === dish.id)
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ dish, quantity: 1 })
    }
  }

  function remove(dishId: number) {
    const idx = items.value.findIndex((i) => i.dish.id === dishId)
    if (idx !== -1) items.value.splice(idx, 1)
  }

  function setQuantity(dishId: number, qty: number) {
    const item = items.value.find((i) => i.dish.id === dishId)
    if (!item) return
    if (qty <= 0) remove(dishId)
    else item.quantity = qty
  }

  function clear() {
    items.value = []
  }

  function open() { isOpen.value = true }
  function close() { isOpen.value = false }
  function toggle() { isOpen.value = !isOpen.value }

  return { items, isOpen, totalItems, totalPrice, add, remove, setQuantity, clear, open, close, toggle }
})
