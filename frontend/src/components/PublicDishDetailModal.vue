<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dish } from '@/types'
import { useCartStore } from '@/stores/cart'

const props = defineProps<{
  dish: Dish | null
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()
const cartStore = useCartStore()

const selection = ref<Record<number, number[]>>({})

watch(() => props.open, (isOpen) => {
  if (isOpen && props.dish) {
    selection.value = {}
    props.dish.modifier_groups?.forEach(g => {
      if (g.is_required && g.max_choices === 1 && g.options.length > 0) {
        selection.value[g.id] = [g.options[0].id]
      } else {
        selection.value[g.id] = []
      }
    })
  }
})

const isValid = computed(() => {
  if (!props.dish || !props.dish.modifier_groups) return true
  for (const g of props.dish.modifier_groups) {
    if (g.is_required && (!selection.value[g.id] || selection.value[g.id].length === 0)) {
      return false
    }
  }
  return true
})

const finalPrice = computed(() => {
  if (!props.dish) return 0
  let total = props.dish.price
  
  if (props.dish.modifier_groups) {
    for (const g of props.dish.modifier_groups) {
      const selectedIds = selection.value[g.id] || []
      for (const optId of selectedIds) {
        const opt = g.options.find(o => o.id === optId)
        if (opt) total += opt.price_delta
      }
    }
  }
  return total
})

function toggleOption(groupId: number, optionId: number, maxChoices: number) {
  if (!selection.value[groupId]) selection.value[groupId] = []
  
  const current = selection.value[groupId]
  const idx = current.indexOf(optionId)
  
  if (maxChoices === 1) {
    selection.value[groupId] = [optionId]
  } else {
    if (idx > -1) {
      current.splice(idx, 1)
    } else {
      if (current.length < maxChoices) {
        current.push(optionId)
      }
    }
  }
}

function addToCart() {
  if (!props.dish || !isValid.value) return
  const selectedOptions = []
  if (props.dish.modifier_groups) {
    for (const g of props.dish.modifier_groups) {
      const selectedIds = selection.value[g.id] || []
      for (const optId of selectedIds) {
        const opt = g.options.find(o => o.id === optId)
        if (opt) selectedOptions.push({ ...opt, group_name: g.name })
      }
    }
  }
  
  cartStore.addItemWithModifiers(props.dish, selectedOptions, finalPrice.value)
  emit('close')
}
</script>

<template>
  <transition name="sheet">
    <div v-if="open && dish" class="modal-overlay" @click.self="$emit('close')">
      <div class="bottom-sheet">
        <div class="sheet-handle"></div>
        <button class="sheet-close" @click="$emit('close')">&times;</button>
        
        <div class="sheet-content">
          <div class="dish-photo-wrap">
            <img v-if="dish.images?.[0]" :src="dish.images[0]" class="dish-photo" />
            <div v-else class="dish-photo-placeholder">🍲</div>
          </div>
          
          <div class="dish-info">
            <h2 class="dish-name">{{ dish.name }}</h2>
            <p class="dish-desc">{{ dish.description }}</p>
          </div>

          <!-- Modifiers -->
          <div class="modifiers" v-if="dish.modifier_groups?.length">
            <div v-for="g in dish.modifier_groups" :key="g.id" class="modifier-group">
              <div class="group-header">
                <h3>{{ g.name }}</h3>
                <span class="group-req" v-if="g.is_required">Обязательно</span>
              </div>
              
              <div class="options-list">
                <label v-for="o in g.options" :key="o.id" class="option-row" :class="{'disabled': g.max_choices > 1 && !selection[g.id]?.includes(o.id) && selection[g.id]?.length >= g.max_choices}">
                  <input 
                    :type="g.max_choices === 1 ? 'radio' : 'checkbox'" 
                    :name="`group_${g.id}`"
                    :checked="selection[g.id]?.includes(o.id)"
                    @change="toggleOption(g.id, o.id, g.max_choices)"
                  />
                  <div class="option-content">
                    <span class="option-name">{{ o.name }}</span>
                    <span class="option-price" v-if="o.price_delta > 0">+{{ o.price_delta }}</span>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="sheet-footer">
          <button class="btn-add" :disabled="!isValid" @click="addToCart">
            {{ t('add') }} • {{ finalPrice }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end; /* Bottom sheet */
  backdrop-filter: blur(2px);
}
.bottom-sheet {
  width: 100%;
  max-height: 90vh;
  background: var(--color-bg);
  border-radius: 20px 20px 0 0;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}
.sheet-handle {
  width: 40px;
  height: 4px;
  background: var(--color-border);
  border-radius: 2px;
  margin: 12px auto;
}
.sheet-close {
  position: absolute;
  top: 12px;
  right: 16px;
  background: var(--color-bg-secondary);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text);
  cursor: pointer;
  z-index: 2;
}
.sheet-content {
  overflow-y: auto;
  padding-bottom: 20px;
}
.dish-photo-wrap {
  width: 100%;
  height: 250px;
  background: var(--color-bg-secondary);
  position: relative;
}
.dish-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.dish-photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
}
.dish-info {
  padding: 20px 20px 0;
}
.dish-name {
  font-size: 24px;
  margin: 0 0 8px;
  font-weight: 500;
}
.dish-desc {
  color: var(--color-text-muted);
  font-size: 14px;
  line-height: 1.4;
  margin: 0;
}
.modifiers {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.group-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}
.group-req {
  font-size: 11px;
  text-transform: uppercase;
  background: var(--color-text);
  color: var(--color-bg);
  padding: 2px 6px;
  border-radius: 4px;
}
.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.option-row {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}
.option-row.disabled {
  opacity: 0.5;
  pointer-events: none;
}
.option-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 12px;
}
.option-row:last-child .option-content {
  border-bottom: none;
  padding-bottom: 0;
}
.option-price {
  color: var(--color-text-muted);
}
.sheet-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg);
}
.btn-add {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  background: var(--color-text);
  color: var(--color-bg);
  font-size: 16px;
  font-weight: 500;
  border: none;
  cursor: pointer;
}
.btn-add:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Transitions */
.sheet-enter-active, .sheet-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.sheet-enter-from .bottom-sheet, .sheet-leave-to .bottom-sheet {
  transform: translateY(100%);
}
.sheet-enter-from, .sheet-leave-to {
  opacity: 0;
}
</style>
