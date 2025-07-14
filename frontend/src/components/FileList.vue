<template>
  <div class="bg-white rounded-lg p-6 shadow-md">
    <div class="flex justify-between items-center mb-5">
      <h3 class="text-lg font-semibold text-gray-800">My Files</h3>
      <button @click="refreshFiles" :disabled="isLoading" class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm">
        {{ isLoading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="isLoading && files.length === 0" class="text-center py-10 text-gray-500 text-lg">
      Loading files...
    </div>

    <div v-else-if="files.length === 0" class="text-center py-10 text-gray-400">
      <p class="mb-2">No files uploaded yet.</p>
      <p class="text-sm">Use the upload section above to add your first file!</p>
    </div>

    <div v-else class="grid gap-4 mb-5">
      <div v-for="file in files" :key="file.id" class="flex items-center gap-4 p-4 border border-gray-200 rounded-lg hover:shadow transition-shadow bg-white">
        <div class="text-3xl opacity-70">📄</div>
        <div class="flex-1 min-w-0">
          <h4 class="font-medium text-base truncate mb-1" :title="file.original_filename">
            {{ file.original_filename }}
          </h4>
          <div class="flex gap-3 text-sm text-gray-500 mb-1">
            <span>{{ formatFileSize(file.file_size) }}</span>
            <span>{{ formatDate(file.created_at) }}</span>
          </div>
          <div v-if="file.content_type" class="text-xs text-gray-400 font-mono">
            {{ file.content_type }}
          </div>
        </div>
        <div class="flex gap-2">
          <button 
            @click="downloadFile(file)"
            :disabled="isDownloading[file.id]"
            class="border border-blue-200 rounded w-9 h-9 flex items-center justify-center text-lg hover:bg-blue-50 hover:border-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {{ isDownloading[file.id] ? '⏳' : '⬇️' }}
          </button>
          <button 
            @click="deleteFile(file)"
            :disabled="isDeleting[file.id]"
            class="border border-red-200 rounded w-9 h-9 flex items-center justify-center text-lg hover:bg-red-50 hover:border-red-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {{ isDeleting[file.id] ? '⏳' : '🗑️' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalFiles > limit" class="flex justify-center items-center gap-4 pt-5 border-t border-gray-100">
      <button 
        @click="prevPage"
        :disabled="currentPage === 1 || isLoading"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        Previous
      </button>
      <span class="text-gray-500 text-sm">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button 
        @click="nextPage"
        :disabled="currentPage === totalPages || isLoading"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
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

<!-- Tutti gli stili sono ora gestiti da Tailwind CSS utility classes nelle classi dei template. -->
