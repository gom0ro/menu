<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { formatPrice, imageUrl } from '@/composables/useOrder'
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

async function deleteImage(index: number) {
  if (!selectedId.value || !editing.value) return
  if (!confirm('Удалить эту фотографию?')) return
  try {
    const updatedDish = await api.deleteDishImage(selectedId.value, editing.value.id, index)
    form.value.images = updatedDish.images || []
    await loadData()
  } catch (err) {
    alert('Не удалось удалить изображение')
  }
}

async function uploadImage(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !selectedId.value || !editing.value) return
  try {
    const updatedDish = await api.uploadDishImage(selectedId.value, editing.value.id, file)
    form.value.images = updatedDish.images || []
    await loadData()
  } catch (err) {
    alert('Не удалось загрузить изображение')
  }
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
      <div class="page__title-wrap">
        <h1>Блюда</h1>
        <p class="page__subtitle" v-if="dishes.length > 0">Управление позициями меню ({{ dishes.length }} блюд)</p>
      </div>
      
      <div class="page__controls">
        <select v-model="selectedId" @change="onRestaurantChange" class="select-control">
          <option v-for="r in restaurants" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
        <button class="btn btn--primary" @click="openCreate">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span>Добавить</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div v-for="n in 3" :key="n" class="skeleton-card skeleton"></div>
    </div>

    <div v-else-if="dishes.length === 0" class="empty-state">
      <div class="empty-state__icon">🍲</div>
      <h3>В меню нет блюд</h3>
      <p>Выберите ресторан или добавьте новые позиции в меню.</p>
      <button class="btn btn--primary" @click="openCreate">Добавить блюдо</button>
    </div>

    <div v-else>
      <!-- Desktop Table View -->
      <div class="table-wrap desktop-only">
        <table class="table">
          <thead>
            <tr>
              <th>Фото</th>
              <th>Название</th>
              <th>Категория</th>
              <th>Цена</th>
              <th>Хит</th>
              <th>Скрыто</th>
              <th>Заказы</th>
              <th class="text-right">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in dishes" :key="d.id">
              <td>
                <div class="dish-photo-cell">
                  <div class="thumb-wrapper">
                    <img v-if="d.images?.[0]" :src="imageUrl(d.images[0])" class="thumb" />
                    <div v-else class="thumb-placeholder">🍲</div>
                  </div>
                  <label class="upload-label" title="Загрузить новое фото">
                    <input type="file" accept="image/*" hidden @change="uploadForDish(d.id, $event)" />
                    📷
                  </label>
                </div>
              </td>
              <td>
                <strong>{{ d.name }}</strong>
                <p class="muted">{{ d.description }}</p>
              </td>
              <td>{{ categories.find(c => c.id === d.category_id)?.name || '—' }}</td>
              <td>{{ formatPrice(d.price, selectedRestaurant?.currency) }}</td>
              <td>
                <span class="badge" :class="{ 'badge--active': d.is_hit }">
                  {{ d.is_hit ? 'Хит' : '—' }}
                </span>
              </td>
              <td>
                <span class="badge" :class="{ 'badge--inactive': d.is_hidden }">
                  {{ d.is_hidden ? 'Скрыто' : 'Нет' }}
                </span>
              </td>
              <td>{{ d.order_count || 0 }}</td>
              <td class="actions text-right">
                <button @click="openEdit(d)" class="btn-action">Изменить</button>
                <button class="btn-action btn-action--danger" @click="remove(d.id)">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Cards Grid -->
      <div class="mobile-only cards-list">
        <div v-for="d in dishes" :key="d.id" class="dish-card">
          <div class="dish-card__main">
            <div class="dish-card__photo-section">
              <div class="thumb-wrapper thumb-wrapper--large">
                <img v-if="d.images?.[0]" :src="imageUrl(d.images[0])" class="thumb" />
                <div v-else class="thumb-placeholder">🍲</div>
              </div>
              <label class="upload-label upload-label--floating" title="Заменить фото">
                <input type="file" accept="image/*" hidden @change="uploadForDish(d.id, $event)" />
                📷
              </label>
            </div>
            
            <div class="dish-card__info">
              <div class="dish-card__header-row">
                <h3 class="dish-card__name">{{ d.name }}</h3>
                <span class="dish-card__price">{{ formatPrice(d.price, selectedRestaurant?.currency) }}</span>
              </div>
              <p class="muted dish-card__desc">{{ d.description }}</p>
              <div class="dish-card__tags">
                <span class="tag-label">{{ categories.find(c => c.id === d.category_id)?.name }}</span>
                <span v-if="d.is_hit" class="status-badge status-badge--active">Хит</span>
                <span v-if="d.is_hidden" class="status-badge">Скрыто</span>
              </div>
            </div>
          </div>

          <div class="dish-card__actions">
            <div class="card-stat">Заказов: <strong>{{ d.order_count || 0 }}</strong></div>
            <button @click="openEdit(d)" class="card-btn card-btn--edit">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              <span>Изменить</span>
            </button>
            <button @click="remove(d.id)" class="card-btn card-btn--danger">
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
              <h2>{{ editing ? 'Редактировать блюдо' : 'Новое блюдо' }}</h2>
              <button type="button" class="close-btn" @click="showForm = false">&times;</button>
            </div>
            
            <div class="modal-form__body">
              <div class="input-group">
                <label for="dish-name">Название *</label>
                <input id="dish-name" v-model="form.name" required placeholder="Например, Стейк Рибай" />
              </div>
              
              <div class="input-group">
                <label for="dish-desc">Описание</label>
                <textarea id="dish-desc" v-model="form.description" rows="3" placeholder="Описание ингредиентов, вес, особенности подачи" />
              </div>

              <div class="input-row-grid">
                <div class="input-group">
                  <label for="dish-price">Цена *</label>
                  <input id="dish-price" v-model.number="form.price" type="number" required min="1" placeholder="4500" />
                </div>
                
                <div class="input-group">
                  <label for="dish-cat">Категория *</label>
                  <select id="dish-cat" v-model="form.category_id" class="select-control">
                    <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </div>
              </div>

              <div class="checkbox-row">
                <label class="checkbox-label-custom">
                  <input v-model="form.is_hit" type="checkbox" />
                  <span>Хит продаж</span>
                </label>
                <label class="checkbox-label-custom">
                  <input v-model="form.is_hidden" type="checkbox" />
                  <span>Скрыть в меню</span>
                </label>
              </div>

              <!-- Photo management section -->
              <div v-if="editing" class="form-images-section">
                <label>Фотографии блюда</label>
                <div class="image-previews">
                  <div v-for="(img, idx) in form.images" :key="idx" class="img-preview-box">
                    <img :src="imageUrl(img)" alt="Фото блюда" />
                    <button type="button" class="img-delete-btn" @click="deleteImage(idx)" title="Удалить фото">&times;</button>
                  </div>
                  <label class="img-upload-box">
                    <input type="file" accept="image/*" hidden @change="uploadImage($event)" />
                    <span>+ Добавить</span>
                  </label>
                </div>
              </div>

              <div v-else class="input-group">
                <label for="dish-image-file">Загрузить фото</label>
                <input id="dish-image-file" type="file" accept="image/*" @change="onFile" />
              </div>
            </div>

            <div class="modal-form__actions">
              <button type="button" class="btn btn--secondary" @click="showForm = false">Отмена</button>
              <button type="submit" class="btn btn--primary">Сохранить</button>
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

.page__controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.select-control {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  color: var(--color-text);
  font-size: 12px;
  outline: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.select-control:focus {
  border-color: var(--color-text);
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
  height: 160px;
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

.dish-photo-cell {
  position: relative;
  display: inline-block;
}

.thumb-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 4px;
  overflow: hidden;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb-wrapper--large {
  width: 64px;
  height: 64px;
}

.thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  font-size: 20px;
}

.upload-label {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  font-size: 11px;
  position: absolute;
  bottom: -6px;
  right: -6px;
  box-shadow: var(--shadow-subtle);
  transition: all var(--transition-fast);
}

.upload-label:hover {
  background: var(--color-hover);
  border-color: var(--color-text);
}

.upload-label--floating {
  bottom: -4px;
  right: -4px;
  width: 28px;
  height: 28px;
  font-size: 13px;
}

.badge {
  display: inline-block;
  padding: 2px 6px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-radius: 4px;
  background: var(--color-hover);
  color: var(--color-text-muted);
}

.badge--active {
  background: rgba(46, 196, 182, 0.1);
  color: #0f9f90;
}

.badge--inactive {
  background: rgba(217, 4, 41, 0.05);
  color: #d90429;
}

.muted {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.text-right {
  text-align: right;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  align-items: center;
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

.btn-action--danger {
  color: #d90429;
}

.btn-action--danger:hover {
  color: #ef233c;
}

/* Responsive layout configurations */
.desktop-only { display: block; }
.mobile-only { display: none; }

/* Mobile Cards View */
.cards-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.dish-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  padding: var(--spacing-md);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.dish-card__main {
  display: flex;
  gap: var(--spacing-md);
}

.dish-card__photo-section {
  position: relative;
  flex-shrink: 0;
}

.dish-card__info {
  flex: 1;
}

.dish-card__header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.dish-card__name {
  font-size: 1.1rem;
  font-weight: 400;
  line-height: 1.2;
}

.dish-card__price {
  font-weight: 500;
  font-size: 14px;
}

.dish-card__desc {
  margin-top: 4px;
}

.dish-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.tag-label {
  font-size: 10px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  padding: 2px 8px;
  border-radius: 10px;
  color: var(--color-text-muted);
}

.status-badge {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 6px;
  background: var(--color-hover);
  color: var(--color-text-muted);
  border-radius: 4px;
}

.status-badge--active {
  background: rgba(46, 196, 182, 0.1);
  color: #0f9f90;
}

.dish-card__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--color-border);
  padding-top: 12px;
  gap: 8px;
}

.card-stat {
  font-size: 11px;
  color: var(--color-text-muted);
  flex: 1;
}

.card-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 12px;
  font-size: 10px;
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

.card-btn--danger {
  color: #d90429;
}

.card-btn--danger:hover {
  background: rgba(217, 4, 41, 0.05);
  border-color: #d90429;
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

.input-row-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.checkbox-row {
  display: flex;
  gap: var(--spacing-md);
  margin: 4px 0;
}

.checkbox-label-custom {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  cursor: pointer;
  color: var(--color-text);
}

.checkbox-label-custom input[type="checkbox"] {
  accent-color: var(--color-text);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

/* Image preview section */
.form-images-section {
  border-top: 1px solid var(--color-border);
  padding-top: var(--spacing-sm);
}

.form-images-section label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  font-weight: 500;
  margin-bottom: 8px;
}

.image-previews {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.img-preview-box {
  position: relative;
  width: 72px;
  height: 72px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.img-preview-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.img-delete-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 18px;
  height: 18px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  line-height: 1;
  transition: background var(--transition-fast);
}

.img-delete-btn:hover {
  background: #d90429;
}

.img-upload-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
  text-align: center;
}

.img-upload-box:hover {
  border-color: var(--color-text);
  color: var(--color-text);
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
  
  .page__controls {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-xs);
  }

  .select-control {
    width: 100%;
  }

  .page__controls .btn {
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
  
  .checkbox-row {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
