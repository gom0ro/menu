import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/menu/:slug',
      name: 'menu',
      component: () => import('@/views/MenuView.vue'),
      meta: { title: 'Меню' },
    },
    {
      path: '/m/:code',
      name: 'short-link',
      component: () => import('@/views/ShortLinkView.vue'),
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/views/admin/DashboardView.vue') },
        { path: 'restaurants', name: 'admin-restaurants', component: () => import('@/views/admin/RestaurantsView.vue') },
        { path: 'dishes', name: 'admin-dishes', component: () => import('@/views/admin/DishesView.vue') },
        { path: 'categories', name: 'admin-categories', component: () => import('@/views/admin/CategoriesView.vue') },
        { path: 'stats', name: 'admin-stats', component: () => import('@/views/admin/StatsView.vue') },
      ],
    },
    {
      path: '/',
      redirect: '/menu/la-maison',
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth) {
    const ok = await auth.checkAuth()
    if (!ok) return { name: 'admin-login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guest && localStorage.getItem('token')) {
    const ok = await auth.checkAuth()
    if (ok) return { name: 'admin-dashboard' }
  }
})

export default router
