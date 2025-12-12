import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SearchView from '../views/SearchView.vue'
import ReviewsView from '../views/ReviewsView.vue'
import RateView from '../views/RateView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/search',
      name: 'search',
      component: SearchView
    },
    {
      path: '/reviews/:teacherId?',
      name: 'reviews',
      component: ReviewsView,
      props: true
    },
    {
      path: '/rate',
      name: 'rate',
      component: RateView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guestOnly: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guestOnly: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAdmin: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView
    }
  ]
})

const authStore = useAuthStore()

router.beforeEach(async (to) => {
  if (!authStore.hasFetchedProfile.value && !authStore.loadingProfile.value) {
    try {
      await authStore.initAuth()
    } catch (error) {
      console.warn('Ошибка инициализации авторизации', error)
    }
  }

  const user = authStore.user.value
  const isAuthenticated = authStore.isAuthenticated.value
  const isAdmin = authStore.isAdmin.value

  if (user.banned && to.name !== 'home') {
    return { name: 'home' }
  }

  if (to.meta.requiresAdmin && !isAdmin) {
    return { name: 'home' }
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && isAuthenticated) {
    return { name: 'home' }
  }

  return true
})

export default router
