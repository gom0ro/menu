<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useRouter } from 'vue-router'

type ManagerEntry = {
  restaurant_id: number
  restaurant_name: string
  restaurant_slug: string
  manager_email: string
  is_active: boolean
}

const router = useRouter()
const managers = ref<ManagerEntry[]>([])
const loading = ref(true)
const error = ref('')
const visiblePasswords = ref<Set<number>>(new Set())
const copiedField = ref<string | null>(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    managers.value = await api.getRestaurantManagers()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

function togglePassword(id: number) {
  if (visiblePasswords.value.has(id)) {
    visiblePasswords.value.delete(id)
  } else {
    visiblePasswords.value.add(id)
  }
  visiblePasswords.value = new Set(visiblePasswords.value)
}

async function copyText(text: string, key: string) {
  await navigator.clipboard.writeText(text)
  copiedField.value = key
  setTimeout(() => { copiedField.value = null }, 1500)
}

function goToRestaurant(slug: string) {
  window.open(`/menu/${slug}`, '_blank')
}

function goToAdminPanel(slug: string) {
  router.push(`/menu/${slug}/admin`)
}

onMounted(load)
</script>

<template>
  <div class="creds-page">
    <div class="creds-page__header">
      <div>
        <h1>Логины менеджеров</h1>
        <p class="creds-page__subtitle">Доступы к панелям управления ресторанов</p>
      </div>
      <button class="btn btn--secondary" @click="load">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
        Обновить
      </button>
    </div>

    <div v-if="loading" class="creds-loading">
      <div v-for="n in 3" :key="n" class="skeleton-row skeleton"></div>
    </div>

    <div v-else-if="error" class="creds-error">
      ⚠ {{ error }}
    </div>

    <div v-else-if="managers.length === 0" class="creds-empty">
      <div class="creds-empty__icon">🔑</div>
      <h3>Нет ресторанов</h3>
      <p>Создайте первый ресторан с учётными данными менеджера на странице Рестораны.</p>
      <router-link to="/admin/restaurants" class="btn btn--primary">Перейти к ресторанам</router-link>
    </div>

    <div v-else>
      <!-- Desktop Table -->
      <div class="table-wrap desktop-only">
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Ресторан</th>
              <th>Статус</th>
              <th>Логин (Email)</th>
              <th>Пароль</th>
              <th>Вход</th>
              <th class="text-right">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(m, idx) in managers" :key="m.restaurant_id">
              <td class="creds-idx">{{ idx + 1 }}</td>
              <td>
                <div class="rest-name-cell">
                  <div class="status-dot" :class="{ 'status-dot--active': m.is_active }"></div>
                  <strong>{{ m.restaurant_name }}</strong>
                </div>
                <code class="rest-slug">/menu/{{ m.restaurant_slug }}</code>
              </td>
              <td>
                <span class="badge" :class="m.is_active ? 'badge--active' : 'badge--inactive'">
                  {{ m.is_active ? 'Активен' : 'Отключён' }}
                </span>
              </td>
              <td>
                <div class="cred-field">
                  <span class="cred-value">{{ m.manager_email }}</span>
                  <button
                    class="copy-btn"
                    :class="{ 'copy-btn--done': copiedField === `email-${m.restaurant_id}` }"
                    @click="copyText(m.manager_email, `email-${m.restaurant_id}`)"
                    title="Копировать"
                  >
                    <svg v-if="copiedField !== `email-${m.restaurant_id}`" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                    <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  </button>
                </div>
              </td>
              <td>
                <div class="cred-field">
                  <span class="cred-value cred-value--password">
                    {{ visiblePasswords.has(m.restaurant_id) ? '(см. при создании)' : '••••••••' }}
                  </span>
                  <button class="copy-btn" @click="togglePassword(m.restaurant_id)" title="Показать/скрыть">
                    <svg v-if="!visiblePasswords.has(m.restaurant_id)" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                    </svg>
                    <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  </button>
                </div>
              </td>
              <td>
                <a href="/admin/login" target="_blank" class="login-link">
                  /admin/login
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
                  </svg>
                </a>
              </td>
              <td class="text-right">
                <div class="actions-row">
                  <button @click="goToRestaurant(m.restaurant_slug)" class="btn-action btn-action--view">Меню</button>
                  <button @click="goToAdminPanel(m.restaurant_slug)" class="btn-action">Панель</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Cards -->
      <div class="mobile-only creds-cards">
        <div v-for="m in managers" :key="m.restaurant_id" class="cred-card">
          <div class="cred-card__header">
            <div class="cred-card__left">
              <div class="status-dot" :class="{ 'status-dot--active': m.is_active }"></div>
              <div>
                <h3 class="cred-card__name">{{ m.restaurant_name }}</h3>
                <code class="cred-card__slug">/menu/{{ m.restaurant_slug }}</code>
              </div>
            </div>
            <span class="badge" :class="m.is_active ? 'badge--active' : 'badge--inactive'">
              {{ m.is_active ? 'Активен' : 'Откл.' }}
            </span>
          </div>

          <div class="cred-card__body">
            <div class="cred-row">
              <span class="cred-label">Логин</span>
              <div class="cred-field">
                <span class="cred-value">{{ m.manager_email }}</span>
                <button
                  class="copy-btn"
                  :class="{ 'copy-btn--done': copiedField === `email-m-${m.restaurant_id}` }"
                  @click="copyText(m.manager_email, `email-m-${m.restaurant_id}`)"
                >
                  <svg v-if="copiedField !== `email-m-${m.restaurant_id}`" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                  <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </button>
              </div>
            </div>
            <div class="cred-row">
              <span class="cred-label">Пароль</span>
              <div class="cred-field">
                <span class="cred-value cred-value--password">
                  {{ visiblePasswords.has(m.restaurant_id) ? '(см. при создании)' : '••••••••' }}
                </span>
                <button class="copy-btn" @click="togglePassword(m.restaurant_id)">
                  <svg v-if="!visiblePasswords.has(m.restaurant_id)" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
            </div>
            <div class="cred-row">
              <span class="cred-label">Ссылка для входа</span>
              <a href="/admin/login" target="_blank" class="login-link">
                /admin/login ↗
              </a>
            </div>
          </div>

          <div class="cred-card__actions">
            <button @click="goToRestaurant(m.restaurant_slug)" class="card-btn">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              </svg>
              Меню
            </button>
            <button @click="goToAdminPanel(m.restaurant_slug)" class="card-btn">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/>
              </svg>
              Панель
            </button>
          </div>
        </div>
      </div>

      <!-- Info note -->
      <div class="creds-note">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        Пароли хранятся в зашифрованном виде. Чтобы сменить пароль менеджеру — удалите и пересоздайте ресторан, или добавьте функцию смены пароля.
      </div>
    </div>
  </div>
</template>

<style scoped>
.creds-page {
  max-width: 1100px;
  margin: 0 auto;
}

.creds-page__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.creds-page__header h1 {
  font-size: 2.25rem;
  font-weight: 300;
  letter-spacing: -0.01em;
  margin-bottom: 4px;
}

.creds-page__subtitle {
  font-size: 13px;
  color: var(--color-text-muted);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
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

/* Loading skeleton */
.creds-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-row {
  height: 56px;
  border-radius: 4px;
}

/* Error / Empty */
.creds-error {
  padding: 16px;
  background: rgba(217, 4, 41, 0.07);
  border: 1px solid rgba(217, 4, 41, 0.2);
  border-radius: 4px;
  color: #d90429;
  font-size: 13px;
}

.creds-empty {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-md);
  border: 1px dashed var(--color-border);
  border-radius: 4px;
}

.creds-empty__icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
}

.creds-empty h3 {
  font-size: 1.5rem;
  margin-bottom: 8px;
}

.creds-empty p {
  color: var(--color-text-muted);
  font-size: 13px;
  max-width: 400px;
  margin: 0 auto var(--spacing-md);
}

/* Desktop Table */
.desktop-only { display: block; }
.mobile-only { display: none; }

.table-wrap {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: var(--spacing-md);
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

.table tbody tr {
  transition: background var(--transition-fast);
}

.table tbody tr:hover {
  background: var(--color-hover);
}

.creds-idx {
  color: var(--color-text-muted);
  font-size: 12px;
  width: 32px;
}

.text-right { text-align: right; }

.rest-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.rest-slug {
  font-size: 11px;
  color: var(--color-text-muted);
}

/* Status */
.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ccc;
  flex-shrink: 0;
}

.status-dot--active {
  background: #2ec4b6;
  box-shadow: 0 0 6px rgba(46, 196, 182, 0.5);
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 10px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-radius: 4px;
  background: var(--color-hover);
  color: var(--color-text-muted);
}

.badge--active {
  background: rgba(46, 196, 182, 0.12);
  color: #0f9f90;
}

.badge--inactive {
  background: rgba(217, 4, 41, 0.07);
  color: #d90429;
}

/* Credential fields */
.cred-field {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 260px;
}

.cred-value {
  font-size: 13px;
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cred-value--password {
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 4px;
  color: var(--color-text-muted);
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.copy-btn:hover {
  background: var(--color-hover);
  color: var(--color-text);
}

.copy-btn--done {
  color: #2ec4b6;
}

.login-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-muted);
  border-bottom: 1px solid transparent;
  transition: all var(--transition-fast);
}

.login-link:hover {
  color: var(--color-text);
  border-color: var(--color-text);
}

/* Actions row in table */
.actions-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-action {
  font-size: 12px;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
}

.btn-action:hover { color: var(--color-text); }

.btn-action--view {
  color: var(--color-text);
}

/* Mobile Cards */
.creds-cards {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.cred-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
}

.cred-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.cred-card__left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cred-card__name {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 2px;
}

.cred-card__slug {
  font-size: 11px;
  color: var(--color-text-muted);
}

.cred-card__body {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cred-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.cred-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.cred-card__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border-top: 1px solid var(--color-border);
}

.card-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
  border-right: 1px solid var(--color-border);
}

.card-btn:last-child { border-right: none; }

.card-btn:hover {
  background: var(--color-hover);
  color: var(--color-text);
}

/* Info note */
.creds-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 12px;
  color: var(--color-text-muted);
  line-height: 1.5;
}

.creds-note svg {
  flex-shrink: 0;
  margin-top: 1px;
}

/* Responsive */
@media (max-width: 768px) {
  .desktop-only { display: none; }
  .mobile-only { display: block; }

  .creds-page__header h1 {
    font-size: 1.75rem;
  }

  .creds-page__header {
    flex-direction: column;
    align-items: stretch;
  }

  .creds-page__header .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
