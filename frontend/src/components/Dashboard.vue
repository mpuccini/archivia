<template>
  <a-layout class="min-h-screen bg-gray-50">
    <a-layout-header style="background: white; padding: 0; height: auto; line-height: normal;">
      <div class="flex justify-between items-center h-16 px-6 border-b border-gray-200">
        <!-- Brand -->
        <div class="flex items-center">
          <span class="text-2xl mr-3">🏛️</span>
          <h1 class="text-xl font-semibold mb-0">Archivia</h1>
        </div>
        <!-- Navbar Tabs -->
        <a-menu
          mode="horizontal"
          :selected-keys="[$route.path]"
          class="flex-1 mx-8 border-0"
          style="background: transparent; line-height: 64px;"
        >
          <a-menu-item key="/dashboard">
            <router-link to="/dashboard">Dashboard</router-link>
          </a-menu-item>
          <a-menu-item key="/guide">
            <router-link to="/guide">Guida</router-link>
          </a-menu-item>
        </a-menu>
        <!-- User info and actions -->
        <div class="flex items-center space-x-4">
          <a-typography-text>
            Ciao, <strong>{{ authStore.user?.username }}</strong>!
          </a-typography-text>
          <a-button
            type="primary"
            danger
            @click="handleLogout"
          >
            Esci
          </a-button>
        </div>
      </div>
    </a-layout-header>

    <!-- Main content -->
    <a-layout-content style="padding: 24px; max-width: 1400px; margin: 0 auto; width: 100%;">
      <DocumentsManager />
    </a-layout-content>
  </a-layout>
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

<style scoped>
.ant-layout-header {
  height: 64px;
  line-height: 64px;
}
</style>
