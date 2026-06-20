import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CartItem, Dish } from '@/types'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const isOpen = ref(false)

  const totalItems = computed(() => items.value.reduce((sum, i) => sum + i.quantity, 0))
  const totalPrice = computed(() => items.value.reduce((sum, i) => sum + i.price * i.quantity, 0))

  function generateId(dishId: number, modifiers?: { id: number }[]): string {
    if (!modifiers || modifiers.length === 0) return dishId.toString()
    const sorted = [...modifiers].sort((a, b) => a.id - b.id)
    return `${dishId}_${sorted.map(m => m.id).join('-')}`
  }

  function add(dish: Dish) {
    addItemWithModifiers(dish, [], dish.price)
  }

  function addItemWithModifiers(dish: Dish, modifiers: { id: number; name: string; price_delta: number; group_name: string }[], price: number) {
    const cartItemId = generateId(dish.id, modifiers)
    const existing = items.value.find((i) => i.cartItemId === cartItemId)
    
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ cartItemId, dish, quantity: 1, price, modifiers })
    }
  }

  function remove(cartItemId: string) {
    const idx = items.value.findIndex((i) => i.cartItemId === cartItemId)
    if (idx !== -1) items.value.splice(idx, 1)
  }

  function setQuantity(cartItemId: string, qty: number) {
    const item = items.value.find((i) => i.cartItemId === cartItemId)
    if (!item) return
    if (qty <= 0) remove(cartItemId)
    else item.quantity = qty
  }

  function clear() {
    items.value = []
  }

  function open() { isOpen.value = true }
  function close() { isOpen.value = false }
  function toggle() { isOpen.value = !isOpen.value }

  return { items, isOpen, totalItems, totalPrice, add, addItemWithModifiers, remove, setQuantity, clear, open, close, toggle }
})
