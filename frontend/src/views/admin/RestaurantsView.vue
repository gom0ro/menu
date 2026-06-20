<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/api/client'
import type { Restaurant } from '@/types'

const restaurants = ref<Restaurant[]>([])
const loading = ref(true)
const showForm = ref(false)
const editing = ref<Restaurant | null>(null)
const formError = ref('')
const saving = ref(false)

const form = ref({
  name: '',
  description: '',
  telegram_username: '',
  whatsapp_phone: '',
  currency: '₸',
  manager_email: '',
  manager_password: '',
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
  formError.value = ''
  form.value = { 
    name: '', 
    description: '', 
    telegram_username: '', 
    whatsapp_phone: '', 
    currency: '₸',
    manager_email: '',
    manager_password: '',
  }
  showForm.value = true
}

function openEdit(r: Restaurant) {
  editing.value = r
  formError.value = ''
  form.value = {
    name: r.name,
    description: r.description || '',
    telegram_username: r.telegram_username || '',
    whatsapp_phone: r.whatsapp_phone || '',
    currency: r.currency,
    manager_email: '',
    manager_password: '',
  }
  showForm.value = true
}

async function save() {
  formError.value = ''
  saving.value = true
  try {
    if (editing.value) {
      await api.updateRestaurant(editing.value.id, form.value)
    } else {
      await api.createRestaurant(form.value)
    }
    showForm.value = false
    await load()
  } catch (e) {
    formError.value = e instanceof Error ? e.message : 'Произошла ошибка'
  } finally {
    saving.value = false
  }
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
      <div class="page__title-wrap">
        <h1>Рестораны</h1>
        <p class="page__subtitle" v-if="restaurants.length > 0">
          Управление вашими точками продаж ({{ restaurants.length }} ресторанов)
        </p>
      </div>
      <button class="btn btn--primary" @click="openCreate">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>Создать</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div v-for="n in 3" :key="n" class="skeleton-card skeleton"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="restaurants.length === 0" class="empty-state">
      <div class="empty-state__icon">🍽</div>
      <h3>Нет добавленных ресторанов</h3>
      <p>Создайте свой первый ресторан, чтобы начать работу с электронным меню.</p>
      <button class="btn btn--primary" @click="openCreate">Создать первый ресторан</button>
    </div>

    <div v-else>
      <!-- Desktop Table View -->
      <div class="table-wrap desktop-only">
        <table class="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Slug</th>
              <th>Короткая ссылка</th>
              <th>QR-код</th>
              <th>Мессенджеры</th>
              <th class="text-right">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in restaurants" :key="r.id">
              <td>
                <div class="restaurant-name-cell">
                  <div class="status-indicator" :class="{ 'status-indicator--active': r.is_active }"></div>
                  <strong>{{ r.name }}</strong>
                </div>
              </td>
              <td><code>{{ r.slug }}</code></td>
              <td>
                <a :href="shortUrl(r.short_code!)" target="_blank" class="link-item">
                  <span>{{ r.short_code }}</span>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15 3 21 3 21 9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                  </svg>
                </a>
              </td>
              <td>
                <button class="link-btn" @click="openQr(r.id)">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="7" height="7"/>
                    <rect x="14" y="3" width="7" height="7"/>
                    <rect x="14" y="14" width="7" height="7"/>
                    <rect x="3" y="14" width="7" height="7"/>
                  </svg>
                  <span>Открыть QR</span>
                </button>
              </td>
              <td class="muted">
                <div class="messengers-list">
                  <span v-if="r.telegram_username" class="messenger-tag">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M21 2L2 9.5l7 3.5 3.5 7L21 2z"/>
                    </svg>
                    @{{ r.telegram_username }}
                  </span>
                  <span v-if="r.whatsapp_phone" class="messenger-tag">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                    </svg>
                    {{ r.whatsapp_phone }}
                  </span>
                  <span v-if="!r.telegram_username && !r.whatsapp_phone">—</span>
                </div>
              </td>
              <td class="actions text-right">
                <a :href="menuUrl(r.slug)" target="_blank" class="btn-action btn-action--view">
                  <span>Меню</span>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="2" y1="12" x2="22" y2="12"/>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                  </svg>
                </a>
                <button @click="openEdit(r)" class="btn-action btn-action--edit">Изменить</button>
                <button class="btn-action btn-action--danger" @click="remove(r.id)">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Cards Grid (Responsive 100x improvement) -->
      <div class="mobile-only cards-list">
        <div v-for="r in restaurants" :key="r.id" class="restaurant-card">
          <div class="restaurant-card__header">
            <div>
              <h3 class="restaurant-card__name">{{ r.name }}</h3>
              <span class="status-badge" :class="{ 'status-badge--active': r.is_active }">
                {{ r.is_active ? 'Активен' : 'Неактивен' }}
              </span>
            </div>
            <div class="restaurant-card__slug">
              <code>{{ r.slug }}</code>
            </div>
          </div>

          <div class="restaurant-card__details">
            <div class="restaurant-card__detail-row">
              <span class="detail-label">Короткая ссылка:</span>
              <a :href="shortUrl(r.short_code!)" target="_blank" class="link-item">
                <span>{{ r.short_code }}</span>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
              </a>
            </div>

            <div class="restaurant-card__detail-row">
              <span class="detail-label">QR-код:</span>
              <button class="link-btn" @click="openQr(r.id)">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                </svg>
                <span>Показать QR</span>
              </button>
            </div>

            <div class="restaurant-card__detail-row" v-if="r.telegram_username || r.whatsapp_phone">
              <span class="detail-label">Мессенджеры:</span>
              <div class="messengers-list">
                <span v-if="r.telegram_username" class="messenger-tag">
                  @{{ r.telegram_username }}
                </span>
                <span v-if="r.whatsapp_phone" class="messenger-tag">
                  {{ r.whatsapp_phone }}
                </span>
              </div>
            </div>
          </div>

          <div class="restaurant-card__actions">
            <a :href="menuUrl(r.slug)" target="_blank" class="card-btn card-btn--view">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="2" y1="12" x2="22" y2="12"/>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              </svg>
              <span>Меню</span>
            </a>
            <button @click="openEdit(r)" class="card-btn card-btn--edit">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              <span>Изменить</span>
            </button>
            <button @click="remove(r.id)" class="card-btn card-btn--danger">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              <span>Удалить</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Responsive Sheet Drawer / Modal Form -->
    <transition name="fade">
      <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
        <div class="modal-container">
          <form class="modal-form" @submit.prevent="save">
            <div class="modal-form__header">
              <h2>{{ editing ? 'Редактировать' : 'Новый ресторан' }}</h2>
              <button type="button" class="close-btn" @click="showForm = false">&times;</button>
            </div>
            
            <div class="modal-form__body">
              <div class="input-group">
                <label for="res-name">Название *</label>
                <input id="res-name" v-model="form.name" required placeholder="Например, La Maison" />
              </div>
              
              <div class="input-group">
                <label for="res-desc">Описание</label>
                <textarea id="res-desc" v-model="form.description" rows="3" placeholder="Краткое описание кухни или концепта" />
              </div>
              
              <div class="input-row-grid">
                <div class="input-group">
                  <label for="res-tg">Telegram username (без @)</label>
                  <div class="input-prefix-wrapper">
                    <span class="input-prefix">@</span>
                    <input id="res-tg" v-model="form.telegram_username" placeholder="restaurant_owner" />
                  </div>
                </div>
                
                <div class="input-group">
                  <label for="res-wa">WhatsApp телефон</label>
                  <input id="res-wa" v-model="form.whatsapp_phone" placeholder="77001234567" />
                </div>
              </div>

              <div class="input-group">
                <label for="res-cur">Валюта</label>
                <input id="res-cur" v-model="form.currency" placeholder="₸" />
              </div>

              <!-- Manager Account Info (only on creation) -->
              <div v-if="!editing" class="input-row-grid" style="border-top: 1px solid var(--color-border); padding-top: 16px; margin-top: 8px;">
                <div class="input-group">
                  <label for="res-manager-email">Email управляющего *</label>
                  <input id="res-manager-email" v-model="form.manager_email" type="email" required placeholder="manager@menu.local" />
                </div>
                <div class="input-group">
                  <label for="res-manager-password">Пароль управляющего *</label>
                  <input id="res-manager-password" v-model="form.manager_password" type="password" required minlength="6" placeholder="••••••••" />
                </div>
              </div>
            </div>

            <div v-if="formError" class="form-error-banner">
              ⚠ {{ formError }}
            </div>

            <div class="modal-form__actions">
              <button type="button" class="btn btn--secondary" @click="showForm = false">Отмена</button>
              <button type="submit" class="btn btn--primary" :disabled="saving">
                {{ saving ? 'Сохраняем...' : 'Сохранить' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.page {
  max-width: 1200px;
  margin: 0 auto;
}

.page__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-md);
}

.page__title-wrap h1 {
  font-size: 2.25rem;
  font-weight: 300;
  letter-spacing: -0.01em;
  margin-bottom: 4px;
}

.page__subtitle {
  font-size: 13px;
  color: var(--color-text-muted);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-weight: 500;
  transition: all var(--transition-fast);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.btn--primary {
  background: var(--color-text);
  color: var(--color-bg);
  border: 1px solid var(--color-text);
}

.btn--primary:hover {
  background: transparent;
  color: var(--color-text);
}

.btn--secondary {
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn--secondary:hover {
  background: var(--color-hover);
  border-color: var(--color-text);
}

/* Loading and Empty State */
.loading-state {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-md);
}

.skeleton-card {
  height: 180px;
  border-radius: 4px;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-md);
  background: var(--color-bg);
  border: 1px dashed var(--color-border);
  border-radius: 4px;
}

.empty-state__icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--color-text-muted);
  max-width: 400px;
  margin: 0 auto var(--spacing-md);
  font-size: 13px;
}

/* Desktop Table View */
.table-wrap {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th, .table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.table th {
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  background: var(--color-bg-secondary);
  font-weight: 500;
}

.table tr:last-child td {
  border-bottom: none;
}

.restaurant-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
}

.status-indicator--active {
  background: #2ec4b6;
  box-shadow: 0 0 8px rgba(46, 196, 182, 0.4);
}

.link-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--color-text);
  font-weight: 500;
  border-bottom: 1px solid transparent;
  transition: all var(--transition-fast);
}

.link-item:hover {
  border-color: var(--color-text);
}

.link-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-muted);
  font-size: 12px;
  transition: color var(--transition-fast);
}

.link-btn:hover {
  color: var(--color-text);
}

.messengers-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.messenger-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  font-size: 11px;
  color: var(--color-text-muted);
}

.text-right {
  text-align: right;
}

.actions {
  text-align: right;
  white-space: nowrap;
}

.actions > * {
  margin-left: 12px;
}

.btn-action {
  font-size: 12px;
  font-weight: 400;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
}

.btn-action:hover {
  color: var(--color-text);
}

.btn-action--view {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--color-text);
}

.btn-action--danger {
  color: #d90429;
}

.btn-action--danger:hover {
  color: #ef233c;
}

/* Responsive design layout configurations */
.desktop-only { display: block; }
.mobile-only { display: none; }

/* Mobile Cards View */
.cards-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.restaurant-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  padding: var(--spacing-md);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.restaurant-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.restaurant-card__name {
  font-size: 1.25rem;
  font-weight: 400;
  margin-bottom: 6px;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  background: var(--color-hover);
  color: var(--color-text-muted);
  font-size: 10px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-radius: 4px;
}

.status-badge--active {
  background: rgba(46, 196, 182, 0.1);
  color: #0f9f90;
}

.restaurant-card__slug {
  font-size: 12px;
}

.restaurant-card__details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  padding: 12px 0;
}

.restaurant-card__detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.detail-label {
  color: var(--color-text-muted);
}

.restaurant-card__actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.card-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}

.card-btn:hover {
  background: var(--color-hover);
  color: var(--color-text);
  border-color: var(--color-text);
}

.card-btn--view {
  color: var(--color-text);
  border-color: var(--color-text);
}

.card-btn--danger {
  color: #d90429;
}

.card-btn--danger:hover {
  background: rgba(217, 4, 41, 0.05);
  border-color: #d90429;
  color: #d90429;
}

/* Modal form drawer styling */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 150;
  backdrop-filter: blur(4px);
}

.modal-container {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  width: min(520px, 92%);
  border-radius: 8px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-form {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.modal-form__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-md) 12px;
  border-bottom: 1px solid var(--color-border);
}

.modal-form__header h2 {
  font-size: 1.5rem;
  font-weight: 300;
}

.close-btn {
  font-size: 24px;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
  line-height: 1;
}

.close-btn:hover {
  color: var(--color-text);
}

.modal-form__body {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 60vh;
  overflow-y: auto;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-group label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  font-weight: 500;
}

.input-group input, .input-group textarea {
  padding: 12px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text);
  outline: none;
  font-size: 13px;
  transition: all var(--transition-fast);
  border-radius: var(--radius-sm);
}

.input-group input:focus, .input-group textarea:focus {
  border-color: var(--color-text);
  background: var(--color-bg);
  box-shadow: 0 0 0 3px var(--color-hover);
}

.input-prefix-wrapper {
  display: flex;
  align-items: center;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.input-prefix {
  padding: 0 12px;
  color: var(--color-text-muted);
  font-size: 13px;
  user-select: none;
}

.input-prefix-wrapper input {
  border: none;
  background: transparent;
  flex: 1;
  padding-left: 0;
}

.input-prefix-wrapper:focus-within {
  border-color: var(--color-text);
  background: var(--color-bg);
  box-shadow: 0 0 0 3px var(--color-hover);
}

.input-row-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.modal-form__actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 12px var(--spacing-md) var(--spacing-md);
  border-top: 1px solid var(--color-border);
}

/* Animations */
@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .desktop-only { display: none; }
  .mobile-only { display: block; }
  
  .page__header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
  }
  
  .page__header .btn {
    width: 100%;
  }

  .modal-overlay {
    align-items: flex-end;
  }
  
  .modal-container {
    width: 100%;
    border-radius: 16px 16px 0 0;
    max-height: 90vh;
    animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .modal-form__body {
    max-height: 50vh;
  }
  
  .input-row-grid {
    grid-template-columns: 1fr;
  }
}

.form-error-banner {
  margin: 0 var(--spacing-md) 12px;
  padding: 10px 14px;
  background: rgba(217, 4, 41, 0.07);
  border: 1px solid rgba(217, 4, 41, 0.25);
  border-radius: var(--radius-sm);
  color: #d90429;
  font-size: 13px;
  line-height: 1.5;
}
</style>
