<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/api/client'
import type { Dish } from '@/types'

const props = defineProps<{
  restaurantId: number
  dish: Dish | null
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'updated'): void
}>()

const form = ref({
  name: '',
  is_required: false,
  max_choices: 1,
  options: [{ name: '', price_delta: 0 }]
})

function addOption() {
  form.value.options.push({ name: '', price_delta: 0 })
}

function removeOption(idx: number) {
  form.value.options.splice(idx, 1)
}

async function createGroup() {
  if (!props.dish) return
  try {
    const validOptions = form.value.options.filter(o => o.name.trim())
    await api.createModifierGroup(props.restaurantId, props.dish.id, {
      ...form.value,
      options: validOptions
    })
    // Reset form
    form.value = {
      name: '',
      is_required: false,
      max_choices: 1,
      options: [{ name: '', price_delta: 0 }]
    }
    emit('updated')
  } catch (e) {
    alert('Ошибка при сохранении')
  }
}

async function deleteGroup(groupId: number) {
  if (!props.dish || !confirm('Удалить эту группу модификаторов?')) return
  await api.deleteModifierGroup(props.restaurantId, props.dish.id, groupId)
  emit('updated')
}
</script>

<template>
  <transition name="fade">
    <div v-if="open && dish" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-container modal-container--large">
        <div class="modal-form__header">
          <h2>Модификаторы: {{ dish.name }}</h2>
          <button type="button" class="close-btn" @click="$emit('close')">&times;</button>
        </div>

        <div class="modal-form__body">
          <!-- Existing groups -->
          <div class="groups-list" v-if="dish.modifier_groups?.length">
            <div v-for="g in dish.modifier_groups" :key="g.id" class="group-card">
              <div class="group-card__header">
                <h3>{{ g.name }} <span class="badge badge--active" v-if="g.is_required">Обязат.</span></h3>
                <button type="button" class="btn-action btn-action--danger" @click="deleteGroup(g.id)">Удалить</button>
              </div>
              <ul class="options-list">
                <li v-for="o in g.options" :key="o.id">
                  {{ o.name }} <span class="muted" v-if="o.price_delta > 0">(+{{ o.price_delta }})</span>
                </li>
              </ul>
            </div>
          </div>
          <p v-else class="muted text-center py-4">Нет модификаторов</p>

          <hr class="divider" />

          <!-- Create new group form -->
          <h3>Добавить группу</h3>
          <form class="new-group-form" @submit.prevent="createGroup">
            <div class="input-row-grid">
              <div class="input-group">
                <label>Название группы</label>
                <input v-model="form.name" required placeholder="Например: Выберите размер" />
              </div>
              <div class="input-group">
                <label>Макс. вариантов</label>
                <input v-model.number="form.max_choices" type="number" min="1" />
              </div>
            </div>
            
            <div class="checkbox-row mb-3 mt-2">
              <label class="checkbox-label-custom">
                <input v-model="form.is_required" type="checkbox" />
                <span>Обязательно для выбора</span>
              </label>
            </div>

            <h4>Опции</h4>
            <div v-for="(opt, idx) in form.options" :key="idx" class="option-row">
              <input v-model="opt.name" placeholder="Название (например: Большой)" required />
              <input v-model.number="opt.price_delta" type="number" placeholder="Доплата (0 = бесплатно)" />
              <button type="button" class="btn-icon" @click="removeOption(idx)" v-if="form.options.length > 1">&times;</button>
            </div>
            <button type="button" class="btn btn--secondary mt-2" @click="addOption">+ Добавить опцию</button>

            <div class="modal-form__actions mt-4">
              <button type="submit" class="btn btn--primary w-full">Создать группу</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 150;
  backdrop-filter: blur(4px);
  padding: var(--spacing-md);
}
.modal-container {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  width: min(520px, 100%);
  border-radius: 12px;
  box-shadow: 0 24px 48px rgba(0,0,0,.18);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 90dvh;
}
.modal-form__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.modal-form__header h2 { font-size: 1.4rem; font-weight: 300; margin: 0; }
.close-btn {
  font-size: 22px;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
}
.close-btn:hover { color: var(--color-text); background: var(--color-hover); }
.modal-form__body {
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  flex: 1;
}
.input-group { display: flex; flex-direction: column; gap: 6px; }
.input-group label {
  font-size: 10px;
  text-transform: uppercase;
  color: var(--color-text-muted);
  font-weight: 500;
}
.input-row-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.checkbox-row { display: flex; gap: var(--spacing-md); margin: 4px 0; }
.checkbox-label-custom {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  cursor: pointer;
}
.modal-form__actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 14px;
}
.modal-container--large {
  max-width: 600px;
  width: 100%;
}
.groups-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}
.group-card {
  border: 1px solid var(--color-border);
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--color-bg-secondary);
}
.group-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.group-card__header h3 {
  margin: 0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.options-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
}
.divider {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 24px 0;
}
.new-group-form {
  background: var(--color-hover);
  padding: 16px;
  border-radius: var(--radius-md);
}
.option-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.option-row input {
  flex: 1;
}
.btn-icon {
  background: transparent;
  border: none;
  font-size: 20px;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0 8px;
}
.mb-3 { margin-bottom: 12px; }
.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 16px; }
.w-full { width: 100%; }
.py-4 { padding: 16px 0; text-align: center; }
</style>
