import type { CartItem } from '@/types'

export function formatPrice(price: number, currency = '₸'): string {
  return `${price.toLocaleString('ru-RU')} ${currency}`
}

export function buildOrderMessage(
  items: CartItem[],
  total: number,
  currency: string,
  customerName: string,
  tableOrAddress: string,
  comment: string,
): string {
  const lines = items.map((i) => `• ${i.dish.name} ×${i.quantity}`)
  const parts = [
    '🍽 Заказ:',
    ...lines,
    '',
    `💰 Итого: ${formatPrice(total, currency)}`,
    '',
    `Имя: ${customerName || '—'}`,
    `Стол/Адрес: ${tableOrAddress || '—'}`,
    `Комментарий: ${comment || '—'}`,
  ]
  return parts.join('\n')
}

export function buildTelegramUrl(username: string, message: string): string {
  const clean = username.replace('@', '')
  return `https://t.me/${clean}?text=${encodeURIComponent(message)}`
}

export function buildWhatsAppUrl(phone: string, message: string): string {
  const clean = phone.replace(/\D/g, '')
  return `https://wa.me/${clean}?text=${encodeURIComponent(message)}`
}

export function imageUrl(path: string): string {
  if (!path) return ''
  if (path.startsWith('http')) return path
  
  const apiUrl = import.meta.env.VITE_API_URL || ''
  if (apiUrl) {
    const baseUrl = apiUrl.replace(/\/api\/?$/, '/')
    return baseUrl + path
  }
  return '/' + path
}
