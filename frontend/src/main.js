import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './assets/css/app.css' // Custom styles and Ant Design customizations

import App from './App.vue'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'
import Guide from './components/Guide.vue'
// Configurazione del router
const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/dashboard', component: Dashboard },
  { path: '/guide', component: Guide }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Configurazione Ant Design con backdrop blur
import { ConfigProvider } from 'ant-design-vue'

// Creazione dell'app
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(Antd)

// Configurazione globale per modal con blur
app.provide('antdConfig', {
  modal: {
    maskStyle: {
      backdropFilter: 'blur(8px)',
      WebkitBackdropFilter: 'blur(8px)',
      backgroundColor: 'rgba(0, 0, 0, 0.60)'
    }
  }
})

app.mount('#app')
