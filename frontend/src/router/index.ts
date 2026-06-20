import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'

const SUPERADMIN_EMAIL = 'admin@menu.local'

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
      meta: { requiresAuth: true, superadminOnly: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/views/admin/DashboardView.vue') },
        { path: 'restaurants', name: 'admin-restaurants', component: () => import('@/views/admin/RestaurantsView.vue') },
        { path: 'dishes', name: 'admin-dishes', component: () => import('@/views/admin/DishesView.vue') },
        { path: 'categories', name: 'admin-categories', component: () => import('@/views/admin/CategoriesView.vue') },
        { path: 'stats', name: 'admin-stats', component: () => import('@/views/admin/StatsView.vue') },
      ],
    },
    // Restaurant manager panel
    {
      path: '/menu/:slug/admin',
      name: 'restaurant-admin',
      component: () => import('@/views/admin/RestaurantAdminView.vue'),
      meta: { requiresAuth: true },
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

/**
 * Helper: resolve the manager's restaurant slug from the API.
 * Returns null if the user is the superadmin or has no restaurant.
 */
async function getManagerSlug(): Promise<string | null> {
  try {
    const restaurants = await api.getRestaurants()
    if (restaurants.length > 0) return restaurants[0].slug
  } catch {
    // ignore
  }
  return null
}

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // ── Auth check ──────────────────────────────────────────────────────────────
  if (to.meta.requiresAuth) {
    const ok = await auth.checkAuth()
    if (!ok) return { name: 'admin-login', query: { redirect: to.fullPath } }
  }

  // ── Guest route (login page): redirect already-authenticated users ──────────
  if (to.meta.guest && localStorage.getItem('token')) {
    const ok = await auth.checkAuth()
    if (ok) {
      if (auth.user?.email === SUPERADMIN_EMAIL) {
        return { name: 'admin-dashboard' }
      }
      // Manager user — redirect to their restaurant admin panel
      const slug = await getManagerSlug()
      if (slug) return { path: `/menu/${slug}/admin` }
      return { name: 'admin-dashboard' }
    }
  }

  // ── Superadmin-only routes: block managers ──────────────────────────────────
  if (to.meta.superadminOnly && auth.user && auth.user.email !== SUPERADMIN_EMAIL) {
    const slug = await getManagerSlug()
    if (slug) return { path: `/menu/${slug}/admin` }
  }
})

export default router
