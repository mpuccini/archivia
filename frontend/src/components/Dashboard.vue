<template>
  <div class="dashboard">
    <header class="header">
      <div class="header-brand">
        <div class="logo">
          🏛️
        </div>
        <h1>Archivia Dashboard</h1>
      </div>
      <div class="user-info">
        <span>Welcome, {{ authStore.user?.username }}!</span>
        <button @click="handleLogout" class="logout-btn">Logout</button>
      </div>
    </header>

    <main class="main-content">
      <!-- Documents Section -->
      <div class="documents-section">
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

<style scoped>
.dashboard {
  min-height: 100vh;
  background: var(--bg-secondary);
}

.header {
  background: var(--nav-bg);
  padding: var(--spacing-lg) var(--spacing-2xl);
  box-shadow: var(--shadow-lg);
  border-bottom: 1px solid var(--nav-bg-dark);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.logo {
  font-size: 2rem;
  filter: brightness(0) invert(1);
}

.header h1 {
  margin: 0;
  color: var(--text-inverse);
  font-size: var(--text-2xl);
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.user-info span {
  color: var(--bg-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
}

.logout-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--accent-danger);
  color: var(--text-inverse);
  border: 1px solid var(--accent-danger);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}

.logout-btn:hover {
  background-color: var(--accent-danger-hover);
  border-color: var(--accent-danger-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.main-content {
  padding: var(--spacing-2xl);
  max-width: 1400px;
  margin: 0 auto;
}

.documents-section {
  margin-bottom: var(--spacing-2xl);
}

@media (max-width: 768px) {
  .header {
    padding: var(--spacing-md) var(--spacing-lg);
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .header-brand {
    align-self: flex-start;
  }
  
  .header h1 {
    font-size: var(--text-xl);
  }
  
  .user-info {
    align-self: flex-end;
  }
  
  .main-content {
    padding: var(--spacing-lg);
  }
}
</style>
