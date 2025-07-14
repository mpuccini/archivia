<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Brand -->
          <div class="flex items-center">
            <span class="text-2xl mr-3">🏛️</span>
            <h1 class="text-xl font-semibold text-gray-900">Archivia</h1>
          </div>
          <!-- Navbar Tabs -->
          <nav class="flex space-x-2">
            <router-link
              to="/dashboard"
              class="px-4 py-2 rounded-md text-sm font-medium"
              :class="$route.path === '/dashboard' ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'"
            >Dashboard</router-link>
            <router-link
              to="/guide"
              class="px-4 py-2 rounded-md text-sm font-medium"
              :class="$route.path === '/guide' ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'"
            >Guida</router-link>
          </nav>
          <!-- User info and actions -->
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-700">
              Welcome, <span class="font-medium">{{ authStore.user?.username }}</span>!
            </span>
            <button
              @click="handleLogout"
              class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
    <main class="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-4 sm:px-0">
        <div class="prose prose-blue max-w-none" v-html="markdownHtml"></div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { marked } from 'marked'

export default {
  name: 'Guide',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const handleLogout = () => {
      authStore.logout()
      router.push('/login')
    }

    const markdownHtml = ref('<p>Caricamento guida...</p>')

    onMounted(async () => {
      try {
        const res = await fetch('/guide.md')
        const md = await res.text()
        markdownHtml.value = marked.parse(md)
      } catch (e) {
        markdownHtml.value = '<p class="text-red-600">Errore nel caricamento della guida.</p>'
      }
    })

    return { authStore, handleLogout, markdownHtml }
  }
}
</script>
