import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { public: true } // Mark this route as public
  },
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/admin/tariffs',
    name: 'tariffs',
    component: () => import('../views/TariffView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  if (!to.meta.public && !isAuthenticated) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
