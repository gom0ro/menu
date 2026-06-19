<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/api/client'
import type { Category, Restaurant } from '@/types'

const restaurants = ref<Restaurant[]>([])
const selectedId = ref<number | null>(null)
const categories = ref<Category[]>([])
const loading = ref(true)
const showForm = ref(false)
const editing = ref<Category | null>(null)

const form = ref({ name: '', sort_order: 0, is_active: true })

async function loadRestaurants() {
  restaurants.value = await api.getRestaurants()
  if (restaurants.value.length && !selectedId.value) {
    selectedId.value = restaurants.value[0].id
  }
}

async function loadCategories() {
  if (!selectedId.value) return
  categories.value = await api.getCategories(selectedId.value)
}

function openCreate() {
  editing.value = null
  form.value = { name: '', sort_order: categories.value.length, is_active: true }
  showForm.value = true
}

function openEdit(c: Category) {
  editing.value = c
  form.value = { name: c.name, sort_order: c.sort_order, is_active: c.is_active }
  showForm.value = true
}

async function save() {
  if (!selectedId.value) return
  if (editing.value) {
    await api.updateCategory(selectedId.value, editing.value.id, form.value)
  } else {
    await api.createCategory(selectedId.value, form.value)
  }
  showForm.value = false
  await loadCategories()
}

async function remove(id: number) {
  if (!selectedId.value || !confirm('Удалить категорию?')) return
  await api.deleteCategory(selectedId.value, id)
  await loadCategories()
}

onMounted(async () => {
  await loadRestaurants()
  await loadCategories()
  loading.value = false
})
</script>

<template>
  <div class="page">
    <div class="page__header">
      <h1>Категории</h1>
      <div class="page__controls">
        <select v-model="selectedId" @change="loadCategories">
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
            <th>Название</th>
            <th>Slug</th>
            <th>Порядок</th>
            <th>Активна</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in categories" :key="c.id">
            <td><strong>{{ c.name }}</strong></td>
            <td><code>{{ c.slug }}</code></td>
            <td>{{ c.sort_order }}</td>
            <td>{{ c.is_active ? '✓' : '—' }}</td>
            <td class="actions">
              <button @click="openEdit(c)">Изменить</button>
              <button class="danger" @click="remove(c.id)">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <form class="modal-form" @submit.prevent="save">
        <h2>{{ editing ? 'Редактировать' : 'Новая категория' }}</h2>
        <label>Название <input v-model="form.name" required /></label>
        <label>Порядок <input v-model.number="form.sort_order" type="number" /></label>
        <label class="checkbox"><input v-model="form.is_active" type="checkbox" /> Активна</label>
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
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--spacing-lg); flex-wrap: wrap; gap: 12px;
}
.page__controls { display: flex; gap: 12px; align-items: center; }
.page__controls select {
  padding: 8px 12px; border: 1px solid var(--color-border);
  background: transparent; color: var(--color-text);
}
.page h1 { font-size: 1.75rem; }
.btn {
  padding: 10px 24px; background: var(--color-text); color: var(--color-bg);
  font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase;
}
.table-wrap { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th, .table td {
  padding: 12px; text-align: left; border-bottom: 1px solid var(--color-border);
}
.table th {
  font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--color-text-muted);
}
.actions { display: flex; gap: 8px; }
.actions button { font-size: 12px; color: var(--color-text-muted); }
.actions button.danger { color: #c44; }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal-form {
  background: var(--color-bg); padding: var(--spacing-lg);
  width: min(400px, 100%); border: 1px solid var(--color-border);
}
.modal-form h2 { margin-bottom: var(--spacing-md); }
.modal-form label {
  display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; font-size: 12px;
}
.modal-form label.checkbox { flex-direction: row; align-items: center; }
.modal-form input {
  padding: 10px; border: 1px solid var(--color-border);
  background: transparent; color: var(--color-text);
}
.modal-form__actions {
  display: flex; gap: 12px; justify-content: flex-end; margin-top: var(--spacing-md);
}
</style>
