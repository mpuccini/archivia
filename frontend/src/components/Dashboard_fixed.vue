<template>
  <div class="dashboard">
    <header class="header">
      <h1>🗂️ Archivia Dashboard</h1>
      <div class="user-info">
        <span>Welcome, {{ authStore.user?.username }}!</span>
        <button @click="handleLogout" class="logout-btn">Logout</button>
      </div>
    </header>
    
    <main class="main-content">
      <!-- Upload Section -->
      <section class="upload-section">
        <FileUpload @upload-complete="handleUploadComplete" />
      </section>

      <!-- Files Section -->
      <section class="files-section">
        <FileList ref="fileListRef" />
      </section>

      <!-- Additional Info Sections -->
      <div class="info-sections">
        <!-- System Status -->
        <div class="card">
          <h3>📊 System Status</h3>
          <div class="status-grid">
            <div class="status-item">
              <span class="status-icon">✅</span>
              <span>Authentication</span>
            </div>
            <div class="status-item">
              <span class="status-icon">✅</span>
              <span>Database</span>
            </div>
            <div class="status-item">
              <span class="status-icon">✅</span>
              <span>File Storage</span>
            </div>
            <div class="status-item">
              <span class="status-icon">✅</span>
              <span>API</span>
            </div>
          </div>
        </div>
        
        <!-- User Information -->
        <div class="card">
          <h3>👤 User Information</h3>
          <div v-if="authStore.user" class="user-details">
            <div class="detail-row">
              <strong>ID:</strong> 
              <span>{{ authStore.user.id }}</span>
            </div>
            <div class="detail-row">
              <strong>Username:</strong> 
              <span>{{ authStore.user.username }}</span>
            </div>
            <div class="detail-row">
              <strong>Email:</strong> 
              <span>{{ authStore.user.email || 'Not set' }}</span>
            </div>
            <div class="detail-row">
              <strong>Account Created:</strong> 
              <span>{{ formatDate(authStore.user.created_at) }}</span>
            </div>
            <div class="detail-row">
              <strong>Status:</strong> 
              <span class="status-active">{{ authStore.user.is_active ? 'Active' : 'Inactive' }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import FileUpload from './FileUpload.vue'
import FileList from './FileList.vue'

export default {
  name: 'Dashboard',
  components: {
    FileUpload,
    FileList
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const fileListRef = ref(null)

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      try {
        const date = new Date(dateString)
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        return `${year}-${month}-${day} ${hours}:${minutes}`
      } catch {
        return dateString
      }
    }

    const handleLogout = () => {
      authStore.logout()
      router.push('/login')
    }

    const handleUploadComplete = () => {
      // Refresh file list when upload completes
      console.log('Upload completed, refreshing file list...')
      if (fileListRef.value && fileListRef.value.refreshFiles) {
        fileListRef.value.refreshFiles()
      }
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
        try {
          await authStore.fetchUser()
        } catch (error) {
          console.error('Failed to fetch user:', error)
        }
      }
    })

    return {
      authStore,
      fileListRef,
      formatDate,
      handleLogout,
      handleUploadComplete
    }
  }
}
</script>

<!-- Tutti gli stili sono ora gestiti da Tailwind CSS utility classes nelle classi dei template. -->
