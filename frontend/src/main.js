import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import router from './router'
import { setupAxiosInterceptors } from './api/axios'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Setup axios interceptors after pinia is initialized
setupAxiosInterceptors()

app.use(router)
app.use(vuetify)

app.mount('#app')
