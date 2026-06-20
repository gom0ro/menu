import { createI18n } from 'vue-i18n'

const messages = {
  ru: {
    menu: 'Меню',
    cart: 'Корзина',
    total: 'Итого',
    add: 'Добавить',
    checkout: 'Оформить заказ',
    emptyCart: 'Ваша корзина пуста',
    search: 'Поиск блюд...',
    chooseOptions: 'Выбрать',
    hit: 'Хит',
    profile: 'Профиль',
    home: 'Главная',
    cancel: 'Отмена',
    comment: 'Комментарий к заказу (опционально)',
    language: 'Язык'
  },
  en: {
    menu: 'Menu',
    cart: 'Cart',
    total: 'Total',
    add: 'Add',
    checkout: 'Checkout',
    emptyCart: 'Your cart is empty',
    search: 'Search dishes...',
    chooseOptions: 'Choose',
    hit: 'Hit',
    profile: 'Profile',
    home: 'Home',
    cancel: 'Cancel',
    comment: 'Order comment (optional)',
    language: 'Language'
  },
  kk: {
    menu: 'Мәзір',
    cart: 'Себет',
    total: 'Барлығы',
    add: 'Қосу',
    checkout: 'Тапсырыс беру',
    emptyCart: 'Себет бос',
    search: 'Тағамдарды іздеу...',
    chooseOptions: 'Таңдау',
    hit: 'Хит',
    profile: 'Профиль',
    home: 'Басты бет',
    cancel: 'Болдырмау',
    comment: 'Тапсырысқа пікір (міндетті емес)',
    language: 'Тіл'
  }
}

const savedLocale = localStorage.getItem('user-locale') || 'ru'

export const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: savedLocale,
  fallbackLocale: 'en',
  messages
})
