<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Brand -->
          <div class="flex items-center">
            <div class="flex-shrink-0 flex items-center">
              <span class="text-2xl mr-3">🏛️</span>
              <h1 class="text-xl font-semibold text-gray-900">Archivia Dashboard</h1>
            </div>
          </div>

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

    <!-- Main content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-4 sm:px-0">
        <DocumentsManager />
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import DocumentsManager from './DocumentsManager.vue'

export default {
  name: 'Dashboard',
  components: {
    DocumentsManager
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const handleLogout = () => {
      authStore.logout()
      router.push('/login')
    }

    onMounted(async () => {
      // Ensure user is authenticated
      await authStore.init()
      if (!authStore.isAuthenticated) {
        router.push('/login')
        return
      }

      // Fetch user info if not already loaded
      if (!authStore.user) {
        await authStore.fetchUser()
      }
    })

    return {
      authStore,
      handleLogout
    }
  }
}
</script>
