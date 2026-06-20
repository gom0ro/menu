<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { formatPrice } from '@/composables/useOrder'
import type { Category, Dish, Restaurant } from '@/types'
import ModifierEditorModal from '@/components/ModifierEditorModal.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const slug = route.params.slug as string
const restaurant = ref<Restaurant | null>(null)
const loading = ref(true)
const activeTab = ref<'categories' | 'dishes' | 'stats'>('dishes')

// Stats state
const stats = ref<import('@/types').Stats | null>(null)
const statsLoading = ref(false)

async function loadStats() {
  if (!restaurant.value) return
  statsLoading.value = true
  try {
    stats.value = await api.getStats(restaurant.value.id)
  } finally {
    statsLoading.value = false
  }
}

// Categories state
const categories = ref<Category[]>([])
const showCategoryForm = ref(false)
const editingCategory = ref<Category | null>(null)
const categoryForm = ref({ name: '', sort_order: 0, is_active: true })

// Dishes state
const dishes = ref<Dish[]>([])
const showDishForm = ref(false)
const showModifierForm = ref(false)
const editingDish = ref<Dish | null>(null)
const editingDishForModifiers = ref<Dish | null>(null)
const dishForm = ref({
  name: '',
  description: '',
  price: 0,
  category_id: 0,
  is_hit: false,
  is_hidden: false,
  sort_order: 0,
  images: [] as string[],
})
const pendingFile = ref<File | null>(null)

// Load restaurant and its data
async function load() {
  loading.value = true
  try {
    const list = await api.getRestaurants()
    const found = list.find((r) => r.slug === slug)
    if (!found) {
      restaurant.value = null
      return
    }
    restaurant.value = found
    await Promise.all([loadCategories(), loadDishes(), loadStats()])
  } finally {
    loading.value = false
  }
}

// Categories Actions
async function loadCategories() {
  if (!restaurant.value) return
  categories.value = await api.getCategories(restaurant.value.id)
}

function openCategoryCreate() {
  editingCategory.value = null
  categoryForm.value = { name: '', sort_order: categories.value.length, is_active: true }
  showCategoryForm.value = true
}

function openCategoryEdit(c: Category) {
  editingCategory.value = c
  categoryForm.value = { name: c.name, sort_order: c.sort_order, is_active: c.is_active }
  showCategoryForm.value = true
}

async function saveCategory() {
  if (!restaurant.value) return
  if (editingCategory.value) {
    await api.updateCategory(restaurant.value.id, editingCategory.value.id, categoryForm.value)
  } else {
    await api.createCategory(restaurant.value.id, categoryForm.value)
  }
  showCategoryForm.value = false
  await loadCategories()
}

async function removeCategory(id: number) {
  if (!restaurant.value || !confirm('Удалить категорию?')) return
  await api.deleteCategory(restaurant.value.id, id)
  await loadCategories()
}

// Dishes Actions
async function loadDishes() {
  if (!restaurant.value) return
  dishes.value = await api.getDishes(restaurant.value.id)
}

function openDishCreate() {
  editingDish.value = null
  dishForm.value = {
    name: '',
    description: '',
    price: 0,
    category_id: categories.value[0]?.id || 0,
    is_hit: false,
    is_hidden: false,
    sort_order: dishes.value.length,
    images: [],
  }
  pendingFile.value = null
  showDishForm.value = true
}

function openDishEdit(d: Dish) {
  editingDish.value = d
  dishForm.value = {
    name: d.name,
    description: d.description || '',
    price: d.price,
    category_id: d.category_id,
    is_hit: d.is_hit,
    is_hidden: d.is_hidden || false,
    sort_order: d.sort_order || 0,
    images: d.images || [],
  }
  pendingFile.value = null
  showDishForm.value = true
}

function openModifierEdit(d: Dish) {
  editingDishForModifiers.value = d
  showModifierForm.value = true
}

async function saveDish() {
  if (!restaurant.value) return
  if (editingDish.value) {
    await api.updateDish(restaurant.value.id, editingDish.value.id, dishForm.value)
  } else {
    const created = await api.createDish(restaurant.value.id, dishForm.value)
    if (pendingFile.value) {
      await api.uploadDishImage(restaurant.value.id, created.id, pendingFile.value)
    }
  }
  pendingFile.value = null
  showDishForm.value = false
  await loadDishes()
}

async function removeDish(id: number) {
  if (!restaurant.value || !confirm('Удалить блюдо?')) return
  await api.deleteDish(restaurant.value.id, id)
  await loadDishes()
}

function onFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) pendingFile.value = file
}

async function uploadForDish(dishId: number, e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !restaurant.value) return
  await api.uploadDishImage(restaurant.value.id, dishId, file)
  await loadDishes()
}

async function deleteImage(index: number) {
  if (!restaurant.value || !editingDish.value) return
  if (!confirm('Удалить эту фотографию?')) return
  try {
    const updatedDish = await api.deleteDishImage(restaurant.value.id, editingDish.value.id, index)
    dishForm.value.images = updatedDish.images || []
    await loadDishes()
  } catch (err) {
    alert('Не удалось удалить изображение')
  }
}

async function uploadImage(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !restaurant.value || !editingDish.value) return
  try {
    const updatedDish = await api.uploadDishImage(restaurant.value.id, editingDish.value.id, file)
    dishForm.value.images = updatedDish.images || []
    await loadDishes()
  } catch (err) {
    alert('Не удалось загрузить изображение')
  }
}

function logout() {
  auth.logout()
  router.push('/admin/login')
}

function publicMenuUrl() {
  return `/menu/${slug}`
}

onMounted(load)
</script>

<template>
  <div class="res-admin" v-if="!loading && restaurant">
    <!-- Header/Top Navigation -->
    <header class="res-admin__header">
      <div class="res-admin__brand-wrap">
        <span class="res-admin__brand">{{ restaurant.name }}</span>
        <span class="res-admin__badge">Панель управления</span>
      </div>

      <nav class="res-admin__tabs">
        <button
          class="res-admin__tab"
          :class="{ 'res-admin__tab--active': activeTab === 'dishes' }"
          @click="activeTab = 'dishes'"
        >
          Блюда
        </button>
        <button
          class="res-admin__tab"
          :class="{ 'res-admin__tab--active': activeTab === 'categories' }"
          @click="activeTab = 'categories'"
        >
          Категории
        </button>
        <button
          class="res-admin__tab"
          :class="{ 'res-admin__tab--active': activeTab === 'stats' }"
          @click="activeTab = 'stats'; loadStats()"
        >
          Статистика
        </button>
      </nav>

      <div class="res-admin__actions">
        <a :href="publicMenuUrl()" target="_blank" class="btn btn--secondary desktop-only">Открыть меню</a>
        <button class="btn btn--logout" @click="logout" aria-label="Выйти">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          <span class="desktop-only">Выйти</span>
        </button>
      </div>
    </header>

    <!-- Main Workspace -->
    <main class="res-admin__main">
      <!-- 1. CATEGORIES TAB PANEL -->
      <div v-if="activeTab === 'categories'" class="page">
        <div class="page__header">
          <div class="page__title-wrap">
            <h2>Категории меню</h2>
            <p class="page__subtitle">Разделы для группировки ваших блюд ({{ categories.length }} категорий)</p>
          </div>
          <button class="btn btn--primary" @click="openCategoryCreate">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            <span>Добавить</span>
          </button>
        </div>

        <div v-if="categories.length === 0" class="empty-state">
          <div class="empty-state__icon">🗂</div>
          <h3>Нет категорий</h3>
          <p>Создайте первую категорию (например, "Пицца" или "Напитки"), чтобы начать заполнять меню.</p>
          <button class="btn btn--primary" @click="openCategoryCreate">Добавить категорию</button>
        </div>

        <div v-else class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Название</th>
                <th>Slug</th>
                <th>Сортировка</th>
                <th>Активна</th>
                <th class="text-right">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in categories" :key="c.id">
                <td><strong>{{ c.name }}</strong></td>
                <td><code>{{ c.slug }}</code></td>
                <td>{{ c.sort_order }}</td>
                <td>
                  <span class="badge" :class="{ 'badge--active': c.is_active }">
                    {{ c.is_active ? 'Активна' : 'Скрыта' }}
                  </span>
                </td>
                <td class="actions text-right">
                  <button @click="openCategoryEdit(c)" class="btn-action">Изменить</button>
                  <button class="btn-action btn-action--danger" @click="removeCategory(c.id)">Удалить</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 2. DISHES TAB PANEL -->
      <div v-if="activeTab === 'dishes'" class="page">
        <div class="page__header">
          <div class="page__title-wrap">
            <h2>Блюда меню</h2>
            <p class="page__subtitle">Позиции, доступные клиентам для заказа ({{ dishes.length }} блюд)</p>
          </div>
          <button class="btn btn--primary" @click="openDishCreate">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            <span>Добавить</span>
          </button>
        </div>

        <div v-if="dishes.length === 0" class="empty-state">
          <div class="empty-state__icon">🍲</div>
          <h3>Нет блюд</h3>
          <p>В меню этого ресторана ещё нет позиций. Нажмите кнопку ниже, чтобы добавить.</p>
          <button class="btn btn--primary" @click="openDishCreate">Добавить блюдо</button>
        </div>

        <div v-else>
          <!-- Desktop dishes table -->
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
                        <img v-if="d.images?.[0]" :src="d.images[0]" class="thumb" />
                        <div v-else class="thumb-placeholder">🍲</div>
                      </div>
                      <label class="upload-label">
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
                  <td>{{ formatPrice(d.price, restaurant?.currency) }}</td>
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
                    <button @click="openModifierEdit(d)" class="btn-action">Модификаторы</button>
                    <button @click="openDishEdit(d)" class="btn-action">Изменить</button>
                    <button class="btn-action btn-action--danger" @click="removeDish(d.id)">Удалить</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Mobile dishes cards grid -->
          <div class="mobile-only cards-list">
            <div v-for="d in dishes" :key="d.id" class="dish-card">
              <div class="dish-card__main">
                <div class="dish-card__photo-section">
                  <div class="thumb-wrapper thumb-wrapper--large">
                    <img v-if="d.images?.[0]" :src="d.images[0]" class="thumb" />
                    <div v-else class="thumb-placeholder">🍲</div>
                  </div>
                  <label class="upload-label upload-label--floating">
                    <input type="file" accept="image/*" hidden @change="uploadForDish(d.id, $event)" />
                    📷
                  </label>
                </div>
                
                <div class="dish-card__info">
                  <div class="dish-card__header-row">
                    <h3 class="dish-card__name">{{ d.name }}</h3>
                    <span class="dish-card__price">{{ formatPrice(d.price, restaurant?.currency) }}</span>
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
                <button @click="openModifierEdit(d)" class="card-btn">Добавки</button>
                <button @click="openDishEdit(d)" class="card-btn card-btn--edit">Изменить</button>
                <button @click="removeDish(d.id)" class="card-btn card-btn--danger">Удалить</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. STATS TAB PANEL -->
      <div v-if="activeTab === 'stats'" class="page stats-page">
        <div class="page__header">
          <div class="page__title-wrap">
            <h2>Статистика</h2>
            <p class="page__subtitle">Аналитика по меню {{ restaurant.name }}</p>
          </div>
          <button class="btn btn--secondary" @click="loadStats" :disabled="statsLoading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 4 23 10 17 10"/>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            Обновить
          </button>
        </div>

        <div v-if="statsLoading" class="stats-loading">
          <div v-for="n in 4" :key="n" class="skeleton skeleton--card"></div>
        </div>

        <template v-else-if="stats">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-card__icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                </svg>
              </div>
              <div class="stat-card__num">{{ stats.menu_views }}</div>
              <div class="stat-card__label">Открытий меню</div>
            </div>
            <div class="stat-card">
              <div class="stat-card__icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/>
                </svg>
              </div>
              <div class="stat-card__num">{{ stats.orders_count }}</div>
              <div class="stat-card__label">Заказов</div>
            </div>
            <div class="stat-card">
              <div class="stat-card__icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 2L2 9.5l7 3.5 3.5 7L21 2z"/>
                </svg>
              </div>
              <div class="stat-card__num">{{ stats.telegram_clicks }}</div>
              <div class="stat-card__label">Telegram переходов</div>
            </div>
            <div class="stat-card">
              <div class="stat-card__icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z"/>
                </svg>
              </div>
              <div class="stat-card__num">{{ stats.whatsapp_clicks }}</div>
              <div class="stat-card__label">WhatsApp переходов</div>
            </div>
          </div>

          <section v-if="stats.popular_dishes.length" class="popular-section">
            <h3 class="popular-section__title">Популярные блюда</h3>
            <div class="table-wrap">
              <table class="table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Блюдо</th>
                    <th>Заказов</th>
                    <th>Цена</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(d, i) in stats.popular_dishes" :key="d.id">
                    <td class="muted">{{ i + 1 }}</td>
                    <td><strong>{{ d.name }}</strong></td>
                    <td>{{ d.order_count }}</td>
                    <td>{{ formatPrice(d.price, restaurant?.currency) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <p v-else class="stats-empty">Нет данных о заказах. Клиенты ещё не использовали меню.</p>
        </template>
      </div>
    </main>

    <!-- Category Form Modal Overlay -->
    <transition name="fade">
      <div v-if="showCategoryForm" class="modal-overlay" @click.self="showCategoryForm = false">
        <div class="modal-container">
          <form class="modal-form" @submit.prevent="saveCategory">
            <div class="modal-form__header">
              <h2>{{ editingCategory ? 'Редактировать категорию' : 'Новая категория' }}</h2>
              <button type="button" class="close-btn" @click="showCategoryForm = false">&times;</button>
            </div>
            
            <div class="modal-form__body">
              <div class="input-group">
                <label for="cat-name">Название *</label>
                <input id="cat-name" v-model="categoryForm.name" required placeholder="Например, Закуски" />
              </div>
              <div class="input-group">
                <label for="cat-order">Порядок отображения</label>
                <input id="cat-order" v-model.number="categoryForm.sort_order" type="number" />
              </div>
              <div class="checkbox-row">
                <label class="checkbox-label-custom">
                  <input v-model="categoryForm.is_active" type="checkbox" />
                  <span>Активна (показывать клиентам)</span>
                </label>
              </div>
            </div>

            <div class="modal-form__actions">
              <button type="button" class="btn btn--secondary" @click="showCategoryForm = false">Отмена</button>
              <button type="submit" class="btn btn--primary">Сохранить</button>
            </div>
          </form>
        </div>
      </div>
    </transition>

    <!-- Dish Form Modal Overlay -->
    <transition name="fade">
      <div v-if="showDishForm" class="modal-overlay" @click.self="showDishForm = false">
        <div class="modal-container">
          <form class="modal-form" @submit.prevent="saveDish">
            <div class="modal-form__header">
              <h2>{{ editingDish ? 'Редактировать блюдо' : 'Новое блюдо' }}</h2>
              <button type="button" class="close-btn" @click="showDishForm = false">&times;</button>
            </div>
            
            <div class="modal-form__body">
              <div class="input-group">
                <label for="dish-name">Название *</label>
                <input id="dish-name" v-model="dishForm.name" required placeholder="Например, Стейк Рибай" />
              </div>
              
              <div class="input-group">
                <label for="dish-desc">Описание</label>
                <textarea id="dish-desc" v-model="dishForm.description" rows="3" placeholder="Описание ингредиентов, вес, особенности подачи" />
              </div>

              <div class="input-row-grid">
                <div class="input-group">
                  <label for="dish-price">Цена *</label>
                  <input id="dish-price" v-model.number="dishForm.price" type="number" required min="1" placeholder="4500" />
                </div>
                
                <div class="input-group">
                  <label for="dish-cat">Категория *</label>
                  <select id="dish-cat" v-model="dishForm.category_id" class="select-control">
                    <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </div>
              </div>

              <div class="checkbox-row">
                <label class="checkbox-label-custom">
                  <input v-model="dishForm.is_hit" type="checkbox" />
                  <span>Хит продаж</span>
                </label>
                <label class="checkbox-label-custom">
                  <input v-model="dishForm.is_hidden" type="checkbox" />
                  <span>Скрыть в меню</span>
                </label>
              </div>

              <!-- Dish Photos management inside form -->
              <div v-if="editingDish" class="form-images-section">
                <label>Фотографии блюда</label>
                <div class="image-previews">
                  <div v-for="(img, idx) in dishForm.images" :key="idx" class="img-preview-box">
                    <img :src="img" alt="Фото блюда" />
                    <button type="button" class="img-delete-btn" @click="deleteImage(idx)" title="Удалить фото">&times;</button>
                  </div>
                  <label class="img-upload-box">
                    <input type="file" accept="image/jpeg, image/png, image/webp, image/jpg" hidden @change="uploadImage($event)" />
                    <span>+ Добавить</span>
                  </label>
                </div>
              </div>

              <div v-else class="input-group">
                <label for="dish-image-file">Загрузить фото</label>
                <input id="dish-image-file" type="file" accept="image/jpeg, image/png, image/webp, image/jpg" @change="onFile" />
              </div>
            </div>

            <div class="modal-form__actions">
              <button type="button" class="btn btn--secondary" @click="showDishForm = false">Отмена</button>
              <button type="submit" class="btn btn--primary">Сохранить</button>
            </div>
          </form>
        </div>
      </div>
    </transition>

    <ModifierEditorModal
      :open="showModifierForm"
      :restaurant-id="restaurant.id"
      :dish="editingDishForModifiers"
      @close="showModifierForm = false"
      @updated="loadDishes"
    />
  </div>

  <div v-else-if="!loading" class="empty-state page-not-found">
    <h2>Ресторан не найден или нет доступа</h2>
    <p>Пожалуйста, проверьте URL-адрес или войдите под правильной учетной записью управляющего.</p>
    <button class="btn btn--primary" @click="router.push('/admin/login')">Войти</button>
  </div>

  <div v-else class="page-loading">
    Загрузка...
  </div>
</template>

<style scoped>
/* ── Root layout ─────────────────────────────────────────── */
.res-admin {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}

/* ── Sticky header ───────────────────────────────────────── */
.res-admin__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  padding: 0 var(--spacing-lg);
  position: sticky;
  top: 0;
  z-index: 110;
  gap: 12px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.res-admin__brand-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.res-admin__brand {
  font-family: var(--font-display);
  font-size: 1.1rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

.res-admin__badge {
  font-size: 9px;
  padding: 2px 6px;
  background: var(--color-hover);
  color: var(--color-text-muted);
  border-radius: var(--radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

/* ── Tab navigation ──────────────────────────────────────── */
.res-admin__tabs {
  display: flex;
  height: 100%;
  flex: 1;
  justify-content: center;
}

.res-admin__tab {
  height: 100%;
  padding: 0 16px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  position: relative;
  transition: color var(--transition-fast);
  white-space: nowrap;
}

.res-admin__tab:hover { color: var(--color-text); }

.res-admin__tab--active {
  color: var(--color-text);
  font-weight: 500;
}

.res-admin__tab--active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-text);
}

/* ── Header actions ──────────────────────────────────────── */
.res-admin__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* ── Buttons ─────────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 9px 18px;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 500;
  transition: all var(--transition-fast);
  border-radius: var(--radius-sm);
  cursor: pointer;
  white-space: nowrap;
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
.btn--secondary:hover { background: var(--color-hover); border-color: var(--color-text); }
.btn--secondary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn--logout {
  padding: 8px;
  color: var(--color-text-muted);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: var(--radius-sm);
}
.btn--logout:hover { color: var(--color-text); background: var(--color-hover); }

/* ── Main content area ───────────────────────────────────── */
.res-admin__main {
  padding: var(--spacing-lg);
  max-width: 1200px;
  margin: 0 auto;
}

/* ── Page section header ─────────────────────────────────── */
.page__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-md);
}

.page__title-wrap h2 {
  font-size: 2rem;
  font-weight: 300;
  letter-spacing: -0.01em;
  margin-bottom: 4px;
}

.page__subtitle {
  font-size: 13px;
  color: var(--color-text-muted);
}

/* ── Responsive helpers ──────────────────────────────────── */
.desktop-only { display: block; }
.mobile-only  { display: none;  }

/* ── Table ───────────────────────────────────────────────── */
.table-wrap {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  overflow: hidden;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th, .table td {
  padding: 14px 16px;
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

.table tr:last-child td { border-bottom: none; }
.table tbody tr { transition: background var(--transition-fast); }
.table tbody tr:hover { background: var(--color-hover); }

.text-right { text-align: right; }

/* ── Dish photo cell ─────────────────────────────────────── */
.dish-photo-cell {
  position: relative;
  display: inline-block;
}

.thumb-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.thumb-wrapper--large { width: 72px; height: 72px; }

.thumb { width: 100%; height: 100%; object-fit: cover; }
.thumb-placeholder { font-size: 18px; }

.upload-label {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  font-size: 10px;
  position: absolute;
  bottom: -5px;
  right: -5px;
  box-shadow: 0 1px 4px rgba(0,0,0,.12);
  transition: all var(--transition-fast);
}
.upload-label:hover { background: var(--color-hover); border-color: var(--color-text); }
.upload-label--floating { bottom: -4px; right: -4px; width: 26px; height: 26px; font-size: 12px; }

/* ── Badges ──────────────────────────────────────────────── */
.badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-radius: 4px;
  background: var(--color-hover);
  color: var(--color-text-muted);
}
.badge--active  { background: rgba(46,196,182,.12); color: #0f9f90; }
.badge--inactive { background: rgba(217,4,41,.07); color: #d90429; }

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
.status-badge--active { background: rgba(46,196,182,.12); color: #0f9f90; }

/* ── Muted text ──────────────────────────────────────────── */
.muted { font-size: 11px; color: var(--color-text-muted); margin-top: 2px; }

/* ── Table action buttons ────────────────────────────────── */
.actions { text-align: right; white-space: nowrap; }
.actions .btn-action { margin-left: 12px; }

.btn-action { font-size: 12px; color: var(--color-text-muted); transition: color var(--transition-fast); }
.btn-action:hover { color: var(--color-text); }
.btn-action--danger { color: #d90429; }
.btn-action--danger:hover { color: #ef233c; }

/* ── Empty state ─────────────────────────────────────────── */
.empty-state {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-md);
  background: var(--color-bg);
  border: 1px dashed var(--color-border);
  border-radius: 6px;
}
.page-not-found { margin: var(--spacing-xl) auto; max-width: 500px; }
.empty-state__icon { font-size: 3rem; margin-bottom: var(--spacing-md); }
.empty-state h3 { font-size: 1.5rem; margin-bottom: 8px; }
.empty-state p { color: var(--color-text-muted); max-width: 400px; margin: 0 auto var(--spacing-md); font-size: 13px; }

/* ╔══════════════════════════════════════════════════════════╗
   ║  DISH CARDS (mobile)                                     ║
   ╚══════════════════════════════════════════════════════════╝ */
.cards-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dish-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
}

.dish-card:hover {
  border-color: color-mix(in srgb, var(--color-border) 60%, var(--color-text) 40%);
  box-shadow: 0 4px 16px rgba(0,0,0,.06);
}

.dish-card__main {
  display: flex;
  gap: 14px;
  padding: 14px;
}

.dish-card__photo-section {
  position: relative;
  flex-shrink: 0;
}

.dish-card__info {
  flex: 1;
  min-width: 0;
}

.dish-card__header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 4px;
}

.dish-card__name {
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.3;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dish-card__price {
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
  color: var(--color-text);
}

.dish-card__desc {
  font-size: 12px;
  color: var(--color-text-muted);
  line-height: 1.4;
  margin-top: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dish-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 10px;
}

.dish-card__actions {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  border-top: 1px solid var(--color-border);
  padding: 10px 14px;
  gap: 8px;
  background: var(--color-bg-secondary);
}

.card-stat {
  font-size: 11px;
  color: var(--color-text-muted);
}

.card-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 7px 14px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}
.card-btn:hover { background: var(--color-hover); color: var(--color-text); border-color: var(--color-text); }
.card-btn--danger { color: #d90429; border-color: transparent; }
.card-btn--danger:hover { background: rgba(217,4,41,.06); border-color: #d90429; }

/* ╔══════════════════════════════════════════════════════════╗
   ║  STATISTICS TAB                                          ║
   ╚══════════════════════════════════════════════════════════╝ */
.stats-page { }

/* Skeleton loader */
.stats-loading {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: var(--spacing-lg);
}
.skeleton {
  background: linear-gradient(90deg, var(--color-bg-secondary) 25%, var(--color-hover) 50%, var(--color-bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 8px;
}
.skeleton--card { height: 110px; }

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Stat cards grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
}

.stat-card:hover {
  border-color: color-mix(in srgb, var(--color-border) 50%, var(--color-text) 50%);
  box-shadow: 0 4px 20px rgba(0,0,0,.06);
}

.stat-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: var(--color-bg-secondary);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}

.stat-card__num {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 300;
  line-height: 1;
  letter-spacing: -0.02em;
}

.stat-card__label {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

/* Popular dishes */
.popular-section {
  margin-top: var(--spacing-xl);
}

.popular-section__title {
  font-size: 1.1rem;
  font-weight: 400;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: var(--spacing-md);
  color: var(--color-text-muted);
}

.stats-empty {
  color: var(--color-text-muted);
  font-size: 13px;
  padding: var(--spacing-xl);
  text-align: center;
  border: 1px dashed var(--color-border);
  border-radius: 6px;
}

/* ╔══════════════════════════════════════════════════════════╗
   ║  MODAL FORMS                                             ║
   ╚══════════════════════════════════════════════════════════╝ */
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

.modal-form { display: flex; flex-direction: column; width: 100%; overflow: hidden; }

.modal-form__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.modal-form__header h2 { font-size: 1.4rem; font-weight: 300; }

.close-btn {
  font-size: 22px;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
  line-height: 1;
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
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
  font-weight: 500;
}
.input-group input, .input-group textarea {
  padding: 11px 13px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text);
  outline: none;
  font-size: 13px;
  transition: all var(--transition-fast);
  border-radius: 6px;
  width: 100%;
}
.input-group input:focus, .input-group textarea:focus {
  border-color: var(--color-text);
  background: var(--color-bg);
  box-shadow: 0 0 0 3px var(--color-hover);
}

.select-control {
  padding: 11px 13px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text);
  outline: none;
  font-size: 13px;
  transition: all var(--transition-fast);
  border-radius: 6px;
  width: 100%;
  cursor: pointer;
}
.select-control:focus {
  border-color: var(--color-text);
  box-shadow: 0 0 0 3px var(--color-hover);
}

.input-row-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.checkbox-row {
  display: flex;
  gap: var(--spacing-md);
  margin: 4px 0;
  flex-wrap: wrap;
}

.checkbox-label-custom {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  cursor: pointer;
  color: var(--color-text);
  user-select: none;
}
.checkbox-label-custom input[type="checkbox"] {
  accent-color: var(--color-text);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

/* Image sections */
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
  display: block;
  margin-bottom: 10px;
}

.image-previews {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.img-preview-box {
  position: relative;
  width: 76px;
  height: 76px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}
.img-preview-box img { width: 100%; height: 100%; object-fit: cover; }

.img-delete-btn {
  position: absolute;
  top: 3px;
  right: 3px;
  width: 20px;
  height: 20px;
  background: rgba(0,0,0,.65);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  cursor: pointer;
  line-height: 1;
  transition: background var(--transition-fast);
}
.img-delete-btn:hover { background: #d90429; }

.img-upload-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 76px;
  height: 76px;
  border: 1.5px dashed var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
  text-align: center;
  flex-shrink: 0;
}
.img-upload-box:hover { border-color: var(--color-text); color: var(--color-text); background: var(--color-hover); }

.modal-form__actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 14px 20px;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}

/* ── Misc ─────────────────────────────────────────────────── */
.page-loading {
  padding: var(--spacing-xl);
  text-align: center;
  color: var(--color-text-muted);
  font-size: 14px;
}

/* ── Slide-up animation (mobile modal) ───────────────────── */
@keyframes slideUp {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}

/* ╔══════════════════════════════════════════════════════════╗
   ║  RESPONSIVE — ≤ 1024px (tablet)                         ║
   ╚══════════════════════════════════════════════════════════╝ */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .stats-loading {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* ╔══════════════════════════════════════════════════════════╗
   ║  RESPONSIVE — ≤ 768px (mobile)                          ║
   ╚══════════════════════════════════════════════════════════╝ */
@media (max-width: 768px) {
  .desktop-only { display: none !important; }
  .mobile-only  { display: block; }

  /* Header compact */
  .res-admin__header {
    height: 56px;
    padding: 0 14px;
    gap: 8px;
  }

  .res-admin__brand {
    font-size: 0.9rem;
    max-width: 100px;
  }

  .res-admin__badge { display: none; }

  .res-admin__tab {
    padding: 0 10px;
    font-size: 10px;
    letter-spacing: 0.04em;
  }

  /* Main content */
  .res-admin__main {
    padding: 14px;
    padding-bottom: 24px;
  }

  /* Page header stacks vertically */
  .page__header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page__header .btn {
    width: 100%;
    justify-content: center;
  }

  .page__title-wrap h2 { font-size: 1.6rem; }

  /* Stats: 2 columns on phone */
  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
  }

  .stats-loading {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .stat-card {
    padding: 16px;
    border-radius: 10px;
    gap: 8px;
  }

  .stat-card__icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
  }

  .stat-card__num { font-size: 2rem; }
  .stat-card__label { font-size: 10px; }

  /* Dish cards full-width */
  .dish-card {
    border-radius: 10px;
  }

  .dish-card__main {
    padding: 12px;
    gap: 12px;
  }

  .dish-card__name { font-size: 0.95rem; }

  .dish-card__actions {
    padding: 8px 12px;
    grid-template-columns: 1fr auto auto;
    gap: 6px;
  }

  .card-btn {
    padding: 7px 12px;
    font-size: 10px;
  }

  /* Modal slides up from bottom */
  .modal-overlay {
    align-items: flex-end;
    padding: 0;
  }

  .modal-container {
    width: 100%;
    border-radius: 18px 18px 0 0;
    max-height: 92dvh;
    animation: slideUp 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .modal-form__body { max-height: unset; }
  .input-row-grid   { grid-template-columns: 1fr; }
  .checkbox-row     { flex-direction: column; gap: 10px; }
}

/* ╔══════════════════════════════════════════════════════════╗
   ║  RESPONSIVE — ≤ 400px (very small)                      ║
   ╚══════════════════════════════════════════════════════════╝ */
@media (max-width: 400px) {
  .res-admin__tab { padding: 0 8px; font-size: 9px; }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-card__num { font-size: 1.75rem; }

  .dish-card__main { flex-direction: column; }

  .thumb-wrapper--large {
    width: 100%;
    height: 160px;
    border-radius: 8px;
  }
}
</style>
