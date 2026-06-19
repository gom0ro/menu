<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { formatPrice } from '@/composables/useOrder'
import type { Category, Dish, Restaurant } from '@/types'

const restaurants = ref<Restaurant[]>([])
const selectedId = ref<number | null>(null)
const categories = ref<Category[]>([])
const dishes = ref<Dish[]>([])
const loading = ref(true)
const showForm = ref(false)
const editing = ref<Dish | null>(null)

const form = ref({
  name: '',
  description: '',
  price: 0,
  category_id: 0,
  is_hit: false,
  is_hidden: false,
  sort_order: 0,
  images: [] as string[],
})

const selectedRestaurant = computed(() =>
  restaurants.value.find((r) => r.id === selectedId.value),
)

async function loadRestaurants() {
  restaurants.value = await api.getRestaurants()
  if (restaurants.value.length && !selectedId.value) {
    selectedId.value = restaurants.value[0].id
  }
}

async function loadData() {
  if (!selectedId.value) return
  const [cats, dishList] = await Promise.all([
    api.getCategories(selectedId.value),
    api.getDishes(selectedId.value),
  ])
  categories.value = cats
  dishes.value = dishList
}

function openCreate() {
  editing.value = null
  form.value = {
    name: '',
    description: '',
    price: 0,
    category_id: categories.value[0]?.id || 0,
    is_hit: false,
    is_hidden: false,
    sort_order: dishes.value.length,
    images: [],
  }
  showForm.value = true
}

function openEdit(d: Dish) {
  editing.value = d
  form.value = {
    name: d.name,
    description: d.description || '',
    price: d.price,
    category_id: d.category_id,
    is_hit: d.is_hit,
    is_hidden: d.is_hidden || false,
    sort_order: d.sort_order || 0,
    images: d.images || [],
  }
  showForm.value = true
}

async function save() {
  if (!selectedId.value) return
  if (editing.value) {
    await api.updateDish(selectedId.value, editing.value.id, form.value)
  } else {
    const created = await api.createDish(selectedId.value, form.value)
    if (pendingFile.value) {
      await api.uploadDishImage(selectedId.value, created.id, pendingFile.value)
    }
  }
  pendingFile.value = null
  showForm.value = false
  await loadData()
}

async function remove(id: number) {
  if (!selectedId.value || !confirm('Удалить блюдо?')) return
  await api.deleteDish(selectedId.value, id)
  await loadData()
}

const pendingFile = ref<File | null>(null)

function onFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) pendingFile.value = file
}

async function uploadForDish(dishId: number, e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !selectedId.value) return
  await api.uploadDishImage(selectedId.value, dishId, file)
  await loadData()
}

onMounted(async () => {
  await loadRestaurants()
  await loadData()
  loading.value = false
})

async function onRestaurantChange() {
  await loadData()
}
</script>

<template>
  <div class="page">
    <div class="page__header">
      <h1>Блюда</h1>
      <div class="page__controls">
        <select v-model="selectedId" @change="onRestaurantChange">
          <option v-for="r in restaurants" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
        <button class="btn" @click="openCreate">+ Добавить</button>
      </div>
    </div>

    <div v-if="loading">Загрузка...</div>

    <div v-else class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>Фото</th>
            <th>Название</th>
            <th>Категория</th>
            <th>Цена</th>
            <th>Хит</th>
            <th>Скрыто</th>
            <th>Заказов</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in dishes" :key="d.id">
            <td>
              <img v-if="d.images?.[0]" :src="d.images[0]" class="thumb" />
              <label class="upload-label">
                <input type="file" accept="image/*" hidden @change="uploadForDish(d.id, $event)" />
                📷
              </label>
            </td>
            <td>
              <strong>{{ d.name }}</strong>
              <p class="muted">{{ d.description }}</p>
            </td>
            <td>{{ categories.find(c => c.id === d.category_id)?.name }}</td>
            <td>{{ formatPrice(d.price, selectedRestaurant?.currency) }}</td>
            <td>{{ d.is_hit ? '✓' : '—' }}</td>
            <td>{{ d.is_hidden ? '✓' : '—' }}</td>
            <td>{{ d.order_count || 0 }}</td>
            <td class="actions">
              <button @click="openEdit(d)">Изменить</button>
              <button class="danger" @click="remove(d.id)">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <form class="modal-form" @submit.prevent="save">
        <h2>{{ editing ? 'Редактировать блюдо' : 'Новое блюдо' }}</h2>
        <label>Название <input v-model="form.name" required /></label>
        <label>Описание <textarea v-model="form.description" rows="2" /></label>
        <label>Цена <input v-model.number="form.price" type="number" required min="1" /></label>
        <label>
          Категория
          <select v-model="form.category_id">
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </label>
        <label class="checkbox"><input v-model="form.is_hit" type="checkbox" /> Хит продаж</label>
        <label class="checkbox"><input v-model="form.is_hidden" type="checkbox" /> Скрыть</label>
        <label v-if="!editing">Фото <input type="file" accept="image/*" @change="onFile" /></label>
        <div class="modal-form__actions">
          <button type="button" @click="showForm = false">Отмена</button>
          <button type="submit" class="btn">Сохранить</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
  gap: 12px;
}

.page__controls { display: flex; gap: 12px; align-items: center; }

.page__controls select {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text);
}

.page h1 { font-size: 1.75rem; }

.btn {
  padding: 10px 24px;
  background: var(--color-text);
  color: var(--color-bg);
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.table-wrap { overflow-x: auto; }

.table { width: 100%; border-collapse: collapse; font-size: 13px; }

.table th, .table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  vertical-align: top;
}

.table th {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.thumb { width: 48px; height: 48px; object-fit: cover; }

.upload-label { cursor: pointer; font-size: 14px; }

.muted { font-size: 11px; color: var(--color-text-muted); margin-top: 2px; }

.actions { display: flex; gap: 8px; white-space: nowrap; }

.actions button { font-size: 12px; color: var(--color-text-muted); }

.actions button.danger { color: #c44; }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: var(--spacing-md);
}

.modal-form {
  background: var(--color-bg); padding: var(--spacing-lg);
  width: min(480px, 100%); border: 1px solid var(--color-border);
  max-height: 90vh; overflow-y: auto;
}

.modal-form h2 { margin-bottom: var(--spacing-md); }

.modal-form label {
  display: flex; flex-direction: column; gap: 4px;
  margin-bottom: 12px; font-size: 12px;
}

.modal-form label.checkbox { flex-direction: row; align-items: center; }

.modal-form input, .modal-form textarea, .modal-form select {
  padding: 10px; border: 1px solid var(--color-border);
  background: transparent; color: var(--color-text);
}

.modal-form__actions {
  display: flex; gap: 12px; justify-content: flex-end; margin-top: var(--spacing-md);
}
</style>
