import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const apiClient = axios.create({
  baseURL: 'http://localhost:5201', // Using the port from Phase 1
  headers: {
    'Content-Type': 'application/json',
  },
})

export const setupAxiosInterceptors = () => {
  const authStore = useAuthStore()
  const token = authStore.token

  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response.status === 401) {
        authStore.logout()
        // Optionally redirect to login
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
  )
}

export default apiClient
