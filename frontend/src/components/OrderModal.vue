<script setup lang="ts">
import { ref } from 'vue'
import {
  buildOrderMessage,
  buildTelegramUrl,
  buildWhatsAppUrl,
  formatPrice,
} from '@/composables/useOrder'
import { api } from '@/api/client'
import type { CartItem } from '@/types'

const props = defineProps<{
  open: boolean
  items: CartItem[]
  total: number
  currency: string
  slug: string
  telegram?: string | null
  whatsapp?: string | null
}>()

const emit = defineEmits<{ close: []; success: [] }>()

const step = ref<'choose' | 'form'>('choose')
const messenger = ref<'telegram' | 'whatsapp'>('telegram')
const name = ref('')
const table = ref('')
const comment = ref('')
const sending = ref(false)

function reset() {
  step.value = 'choose'
  name.value = ''
  table.value = ''
  comment.value = ''
}

function close() {
  reset()
  emit('close')
}

function selectMessenger(m: 'telegram' | 'whatsapp') {
  messenger.value = m
  step.value = 'form'
}

async function sendOrder() {
  sending.value = true
  try {
    const message = buildOrderMessage(
      props.items,
      props.total,
      props.currency,
      name.value,
      table.value,
      comment.value,
    )

    await api.trackOrder(
      props.slug,
      props.items.map((i) => ({ dish_id: i.dish.id, quantity: i.quantity })),
      messenger.value,
    )

    let url: string
    if (messenger.value === 'telegram' && props.telegram) {
      url = buildTelegramUrl(props.telegram, message)
    } else if (messenger.value === 'whatsapp' && props.whatsapp) {
      url = buildWhatsAppUrl(props.whatsapp, message)
    } else {
      alert('Мессенджер не настроен')
      return
    }

    window.open(url, '_blank')
    emit('success')
    reset()
    emit('close')
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <transition name="fade">
      <div v-if="open" class="modal-backdrop" @click="close" />
    </transition>
    <transition name="fade">
      <div v-if="open" class="modal" role="dialog">
        <div class="modal__glass">
          <button class="modal__close" @click="close">✕</button>

          <template v-if="step === 'choose'">
            <h2 class="modal__title">Куда отправить заказ?</h2>
            <p class="modal__subtitle">Итого: {{ formatPrice(total, currency) }}</p>
            <div class="modal__choices">
              <button
                class="modal__choice"
                :disabled="!telegram"
                @click="selectMessenger('telegram')"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 0 0-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/>
                </svg>
                Telegram
              </button>
              <button
                class="modal__choice"
                :disabled="!whatsapp"
                @click="selectMessenger('whatsapp')"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/>
                </svg>
                WhatsApp
              </button>
            </div>
          </template>

          <template v-else>
            <h2 class="modal__title">Детали заказа</h2>
            <div class="modal__preview">
              <p v-for="item in items" :key="item.dish.id">
                • {{ item.dish.name }} ×{{ item.quantity }}
              </p>
              <p class="modal__total">💰 Итого: {{ formatPrice(total, currency) }}</p>
            </div>
            <form class="modal__form" @submit.prevent="sendOrder">
              <label>
                <span>Имя</span>
                <input v-model="name" type="text" placeholder="Ваше имя" />
              </label>
              <label>
                <span>Стол / Адрес</span>
                <input v-model="table" type="text" placeholder="Стол 5 или адрес доставки" />
              </label>
              <label>
                <span>Комментарий</span>
                <textarea v-model="comment" rows="2" placeholder="Пожелания к заказу" />
              </label>
              <button type="submit" class="modal__submit" :disabled="sending">
                {{ sending ? 'Отправка...' : `Отправить в ${messenger === 'telegram' ? 'Telegram' : 'WhatsApp'}` }}
              </button>
              <button type="button" class="modal__back" @click="step = 'choose'">← Назад</button>
            </form>
          </template>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 300;
  backdrop-filter: blur(4px);
}

.modal {
  position: fixed;
  inset: 0;
  z-index: 301;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md);
  pointer-events: none;
}

.modal__glass {
  pointer-events: auto;
  width: min(480px, 100%);
  padding: var(--spacing-lg);
  background: var(--color-glass);
  backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid var(--color-glass-border);
  border-radius: 4px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.12);
  position: relative;
}

.modal__close {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 18px;
  color: var(--color-text-muted);
}

.modal__title {
  font-size: 1.5rem;
  text-align: center;
  margin-bottom: 8px;
  letter-spacing: 0.04em;
}

.modal__subtitle {
  text-align: center;
  color: var(--color-text-muted);
  font-size: 13px;
  margin-bottom: var(--spacing-lg);
}

.modal__choices {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal__choice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  border: 1px solid var(--color-border);
  font-size: 13px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transition: all var(--transition-fast);
}

.modal__choice:hover:not(:disabled) {
  background: var(--color-text);
  color: var(--color-bg);
  border-color: var(--color-text);
}

.modal__choice:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.modal__preview {
  background: var(--color-bg-secondary);
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  font-size: 13px;
  line-height: 1.8;
}

.modal__total {
  margin-top: 8px;
  font-weight: 500;
}

.modal__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal__form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.modal__form label span {
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.modal__form input,
.modal__form textarea {
  padding: 12px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text);
  border-radius: var(--radius-sm);
}

.modal__form input:focus,
.modal__form textarea:focus {
  outline: none;
  border-color: var(--color-text);
}

.modal__submit {
  padding: 16px;
  background: var(--color-text);
  color: var(--color-bg);
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-top: 8px;
}

.modal__submit:disabled { opacity: 0.6; }

.modal__back {
  text-align: center;
  font-size: 12px;
  color: var(--color-text-muted);
  padding: 8px;
}
</style>
