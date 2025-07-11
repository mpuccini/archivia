<template>
  <div class="file-list">
    <div class="header">
      <h3>My Files</h3>
      <button @click="refreshFiles" :disabled="isLoading" class="refresh-btn">
        {{ isLoading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="isLoading && files.length === 0" class="loading">
      Loading files...
    </div>

    <div v-else-if="files.length === 0" class="empty-state">
      <p>No files uploaded yet.</p>
      <p>Use the upload section above to add your first file!</p>
    </div>

    <div v-else class="files-grid">
      <div v-for="file in files" :key="file.id" class="file-card">
        <div class="file-icon">
          📄
        </div>
        <div class="file-info">
          <h4 class="file-name" :title="file.original_filename">
            {{ file.original_filename }}
          </h4>
          <div class="file-details">
            <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
            <span class="file-date">{{ formatDate(file.created_at) }}</span>
          </div>
          <div v-if="file.content_type" class="file-type">
            {{ file.content_type }}
          </div>
        </div>
        <div class="file-actions">
          <button 
            @click="downloadFile(file)"
            :disabled="isDownloading[file.id]"
            class="download-btn"
          >
            {{ isDownloading[file.id] ? '⏳' : '⬇️' }}
          </button>
          <button 
            @click="deleteFile(file)"
            :disabled="isDeleting[file.id]"
            class="delete-btn"
          >
            {{ isDeleting[file.id] ? '⏳' : '🗑️' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalFiles > limit" class="pagination">
      <button 
        @click="prevPage"
        :disabled="currentPage === 1 || isLoading"
        class="page-btn"
      >
        Previous
      </button>
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button 
        @click="nextPage"
        :disabled="currentPage === totalPages || isLoading"
        class="page-btn"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

export default {
  name: 'FileList',
  setup() {
    const authStore = useAuthStore()
    const files = ref([])
    const isLoading = ref(false)
    const isDownloading = reactive({})
    const isDeleting = reactive({})
    const currentPage = ref(1)
    const limit = ref(20)
    const totalFiles = ref(0)

    const totalPages = computed(() => {
      return Math.ceil(totalFiles.value / limit.value)
    })

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const refreshFiles = async () => {
      isLoading.value = true
      try {
        const skip = (currentPage.value - 1) * limit.value
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/files/?skip=${skip}&limit=${limit.value}`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          }
        )
        files.value = response.data
        // Note: Backend doesn't return total count yet, we'll estimate it
        totalFiles.value = response.data.length === limit.value ? 
          (currentPage.value * limit.value) + 1 : 
          ((currentPage.value - 1) * limit.value) + response.data.length
      } catch (error) {
        console.error('Error fetching files:', error)
        alert('Failed to load files: ' + (error.response?.data?.detail || error.message))
      } finally {
        isLoading.value = false
      }
    }

    const downloadFile = async (file) => {
      isDownloading[file.id] = true
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/files/${file.id}/stream`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          }
        )
        
        if (!response.ok) throw new Error('Download failed')
        
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = file.filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } catch (error) {
        console.error('Error downloading file:', error)
        alert('Failed to download file: ' + (error.response?.data?.detail || error.message))
      } finally {
        delete isDownloading[file.id]
      }
    }

    const deleteFile = async (file) => {
      if (!confirm(`Are you sure you want to delete "${file.original_filename}"?`)) {
        return
      }

      isDeleting[file.id] = true
      try {
        await axios.delete(
          `${import.meta.env.VITE_API_URL}/files/${file.id}`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          }
        )
        
        // Remove file from list
        files.value = files.value.filter(f => f.id !== file.id)
        totalFiles.value--
      } catch (error) {
        console.error('Error deleting file:', error)
        alert('Failed to delete file: ' + (error.response?.data?.detail || error.message))
      } finally {
        delete isDeleting[file.id]
      }
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        refreshFiles()
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        refreshFiles()
      }
    }

    onMounted(() => {
      refreshFiles()
    })

    return {
      files,
      isLoading,
      isDownloading,
      isDeleting,
      currentPage,
      limit,
      totalFiles,
      totalPages,
      formatFileSize,
      formatDate,
      refreshFiles,
      downloadFile,
      deleteFile,
      prevPage,
      nextPage
    }
  }
}
</script>

<style scoped>
.file-list {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.refresh-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:hover:not(:disabled) {
  background: #5a6268;
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.files-grid {
  display: grid;
  gap: 16px;
  margin-bottom: 20px;
}

.file-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  transition: box-shadow 0.3s;
}

.file-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.file-icon {
  font-size: 32px;
  opacity: 0.7;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-details {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 4px;
}

.file-type {
  font-size: 12px;
  color: #6c757d;
  font-family: monospace;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.download-btn, .delete-btn {
  background: none;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.download-btn:hover:not(:disabled) {
  background: #e3f2fd;
  border-color: #2196f3;
}

.delete-btn:hover:not(:disabled) {
  background: #ffebee;
  border-color: #f44336;
}

.download-btn:disabled, .delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.page-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.page-info {
  color: #6c757d;
  font-size: 14px;
}
</style>
