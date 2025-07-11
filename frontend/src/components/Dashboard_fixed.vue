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
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
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

<style scoped>
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.header {
  background: white;
  border-radius: 12px;
  padding: 20px 30px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  color: #2d3748;
  font-size: 28px;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info span {
  color: #4a5568;
  font-weight: 500;
}

.logout-btn {
  background: #e53e3e;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background: #c53030;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
}

.upload-section {
  margin-bottom: 30px;
}

.files-section {
  margin-bottom: 30px;
}

.info-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card h3 {
  margin: 0 0 20px 0;
  color: #2d3748;
  font-size: 18px;
  font-weight: 600;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #f7fafc;
  border-radius: 8px;
}

.status-icon {
  font-size: 16px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row strong {
  color: #4a5568;
  font-weight: 600;
}

.detail-row span {
  color: #2d3748;
}

.status-active {
  color: #38a169;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }

  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .info-sections {
    grid-template-columns: 1fr;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>
