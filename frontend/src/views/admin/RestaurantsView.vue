<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/api/client'
import type { Restaurant } from '@/types'

const restaurants = ref<Restaurant[]>([])
const loading = ref(true)
const showForm = ref(false)
const editing = ref<Restaurant | null>(null)

const form = ref({
  name: '',
  description: '',
  telegram_username: '',
  whatsapp_phone: '',
  currency: '₸',
})

async function load() {
  loading.value = true
  try {
    restaurants.value = await api.getRestaurants()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.value = { name: '', description: '', telegram_username: '', whatsapp_phone: '', currency: '₸' }
  showForm.value = true
}

function openEdit(r: Restaurant) {
  editing.value = r
  form.value = {
    name: r.name,
    description: r.description || '',
    telegram_username: r.telegram_username || '',
    whatsapp_phone: r.whatsapp_phone || '',
    currency: r.currency,
  }
  showForm.value = true
}

async function save() {
  if (editing.value) {
    await api.updateRestaurant(editing.value.id, form.value)
  } else {
    await api.createRestaurant(form.value)
  }
  showForm.value = false
  await load()
}

async function remove(id: number) {
  if (!confirm('Удалить ресторан?')) return
  await api.deleteRestaurant(id)
  await load()
}

function menuUrl(slug: string) {
  return `${window.location.origin}/menu/${slug}`
}

function shortUrl(code: string) {
  return `${window.location.origin}/m/${code}`
}

function qrUrl(id: number) {
  return api.getQrUrl(id, window.location.origin)
}

async function openQr(id: number) {
  const token = localStorage.getItem('token')
  const res = await fetch(qrUrl(id), {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!res.ok) return
  const blob = await res.blob()
  window.open(URL.createObjectURL(blob), '_blank')
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page__header">
      <h1>Рестораны</h1>
      <button class="btn" @click="openCreate">+ Создать</button>
    </div>

    <div v-if="loading">Загрузка...</div>

    <div v-else class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Slug</th>
            <th>Короткая ссылка</th>
            <th>QR</th>
            <th>Мессенджеры</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in restaurants" :key="r.id">
            <td><strong>{{ r.name }}</strong></td>
            <td><code>{{ r.slug }}</code></td>
            <td>
              <a :href="shortUrl(r.short_code!)" target="_blank" class="link">{{ r.short_code }}</a>
            </td>
            <td>
              <button class="link" @click="openQr(r.id)">QR-код</button>
            </td>
            <td class="muted">
              {{ r.telegram_username ? '@' + r.telegram_username : '—' }} /
              {{ r.whatsapp_phone || '—' }}
            </td>
            <td class="actions">
              <a :href="menuUrl(r.slug)" target="_blank" class="link">Меню</a>
              <button @click="openEdit(r)">Изменить</button>
              <button class="danger" @click="remove(r.id)">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <form class="modal-form" @submit.prevent="save">
        <h2>{{ editing ? 'Редактировать' : 'Новый ресторан' }}</h2>
        <label>Название <input v-model="form.name" required /></label>
        <label>Описание <textarea v-model="form.description" rows="2" /></label>
        <label>Telegram username <input v-model="form.telegram_username" placeholder="restaurant_owner" /></label>
        <label>WhatsApp телефон <input v-model="form.whatsapp_phone" placeholder="77001234567" /></label>
        <label>Валюта <input v-model="form.currency" /></label>
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

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th, .table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.table th {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.muted { color: var(--color-text-muted); font-size: 12px; }

.actions { display: flex; gap: 8px; white-space: nowrap; }

.actions button {
  font-size: 12px;
  color: var(--color-text-muted);
}

.actions button.danger { color: #c44; }

.link { font-size: 12px; text-decoration: underline; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: var(--spacing-md);
}

.modal-form {
  background: var(--color-bg);
  padding: var(--spacing-lg);
  width: min(480px, 100%);
  border: 1px solid var(--color-border);
}

.modal-form h2 { margin-bottom: var(--spacing-md); }

.modal-form label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
  font-size: 12px;
}

.modal-form input, .modal-form textarea {
  padding: 10px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text);
}

.modal-form__actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: var(--spacing-md);
}
</style>
