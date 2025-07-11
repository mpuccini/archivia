<template>
  <div class="file-upload">
    <h3>Upload File</h3>
    
    <!-- File Selection -->
    <div class="upload-section">
      <input 
        ref="fileInput"
        type="file" 
        @change="handleFileSelect"
        :disabled="isUploading"
        class="file-input"
        multiple
      />
      <button 
        @click="$refs.fileInput.click()"
        class="select-btn"
        :disabled="isUploading"
      >
        Select Files
      </button>
    </div>

    <!-- Selected Files -->
    <div v-if="selectedFiles.length > 0" class="selected-files">
      <h4>Selected Files:</h4>
      <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
        <div class="file-info">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">({{ formatFileSize(file.size) }})</span>
        </div>
        <button 
          @click="removeFile(index)"
          class="remove-btn"
          :disabled="isUploading"
        >
          ×
        </button>
      </div>
    </div>

    <!-- Upload Button -->
    <div v-if="selectedFiles.length > 0" class="upload-actions">
      <button 
        @click="startUpload"
        :disabled="isUploading"
        class="upload-btn"
      >
        {{ isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} File${selectedFiles.length > 1 ? 's' : ''}` }}
      </button>
    </div>

    <!-- Upload Progress -->
    <div v-if="isUploading" class="upload-progress">
      <div v-for="upload in activeUploads" :key="upload.id" class="upload-item">
        <div class="upload-header">
          <span class="upload-filename">{{ upload.filename }}</span>
          <span class="upload-status">{{ upload.status }}</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: upload.progress + '%' }"
          ></div>
        </div>
        <div class="upload-details">
          {{ upload.progress.toFixed(1) }}% - {{ upload.speed }}
        </div>
      </div>
    </div>

    <!-- Upload Results -->
    <div v-if="uploadResults.length > 0" class="upload-results">
      <h4>Upload Results:</h4>
      <div v-for="result in uploadResults" :key="result.id" class="result-item">
        <span class="result-filename">{{ result.filename }}</span>
        <span 
          class="result-status"
          :class="{ 'success': result.success, 'error': !result.success }"
        >
          {{ result.success ? '✅ Success' : '❌ Failed' }}
        </span>
        <span v-if="!result.success" class="result-error">{{ result.error }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

export default {
  name: 'FileUpload',
  setup() {
    const authStore = useAuthStore()
    const selectedFiles = ref([])
    const isUploading = ref(false)
    const activeUploads = reactive([])
    const uploadResults = reactive([])

    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      selectedFiles.value = [...selectedFiles.value, ...files]
    }

    const removeFile = (index) => {
      selectedFiles.value.splice(index, 1)
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const createUploadTracker = (file) => {
      return {
        id: Date.now() + Math.random(),
        filename: file.name,
        status: 'Initializing...',
        progress: 0,
        speed: '0 KB/s'
      }
    }

    const updateUploadProgress = (trackerId, progress, status, speed = null) => {
      const upload = activeUploads.find(u => u.id === trackerId)
      if (upload) {
        upload.progress = progress
        upload.status = status
        if (speed) upload.speed = speed
      }
    }

    const startUpload = async () => {
      if (selectedFiles.value.length === 0) return

      isUploading.value = true
      uploadResults.length = 0
      activeUploads.length = 0

      for (const file of selectedFiles.value) {
        const tracker = createUploadTracker(file)
        activeUploads.push(tracker)

        try {
          await uploadFile(file, tracker)
          uploadResults.push({
            id: tracker.id,
            filename: file.name,
            success: true
          })
        } catch (error) {
          uploadResults.push({
            id: tracker.id,
            filename: file.name,
            success: false,
            error: error.message
          })
        }
      }

      isUploading.value = false
      selectedFiles.value = []
      // Clear file input
      const fileInput = document.querySelector('.file-input')
      if (fileInput) fileInput.value = ''
    }

    const uploadFile = async (file, tracker) => {
      const CHUNK_SIZE = 64 * 1024 * 1024 // 64MB chunks
      const isLargeFile = file.size > CHUNK_SIZE

      updateUploadProgress(tracker.id, 0, 'Initiating upload...')

      try {
        // Step 1: Initiate upload
        const formData = new FormData()
        formData.append('filename', file.name)
        formData.append('file_size', file.size.toString())
        formData.append('content_type', file.type || 'application/octet-stream')
        
        const initResponse = await axios.post(
          `${import.meta.env.VITE_API_URL}/files/upload/initiate`,
          formData,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          }
        )

        const { file_id, is_multipart, chunk_size, total_chunks } = initResponse.data

        if (is_multipart) {
          // Multipart upload for large files
          await uploadMultipart(file, file_id, chunk_size, total_chunks, tracker)
        } else {
          // Single upload for small files
          await uploadSingle(file, file_id, tracker)
        }

      } catch (error) {
        updateUploadProgress(tracker.id, 0, 'Failed')
        throw new Error(error.response?.data?.detail || error.message)
      }
    }

    const uploadSingle = async (file, fileId, tracker) => {
      updateUploadProgress(tracker.id, 10, 'Uploading file...')

      const formData = new FormData()
      formData.append('file', file)

      await axios.post(
        `${import.meta.env.VITE_API_URL}/files/upload/single/${fileId}`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            updateUploadProgress(tracker.id, progress, 'Uploading...')
          }
        }
      )

      updateUploadProgress(tracker.id, 100, 'Completed')
    }

    const uploadMultipart = async (file, fileId, chunkSize, totalChunks, tracker) => {
      const parts = []
      
      updateUploadProgress(tracker.id, 5, `Uploading ${totalChunks} chunks...`)

      // Upload chunks
      for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize
        const end = Math.min(start + chunkSize, file.size)
        const chunk = file.slice(start, end)

        const formData = new FormData()
        formData.append('chunk', chunk)
        formData.append('chunk_number', i + 1)

        const chunkResponse = await axios.post(
          `${import.meta.env.VITE_API_URL}/files/upload/chunk/${fileId}`,
          formData,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'multipart/form-data'
            }
          }
        )

        // Note: In a real implementation, you'd need to handle the presigned URL
        // For now, we'll simulate the chunk upload
        parts.push({
          PartNumber: i + 1,
          ETag: `"chunk-${i + 1}"`
        })

        const progress = Math.round(((i + 1) / totalChunks) * 90) + 5
        updateUploadProgress(
          tracker.id, 
          progress, 
          `Chunk ${i + 1}/${totalChunks} uploaded`
        )
      }

      // Complete multipart upload
      updateUploadProgress(tracker.id, 95, 'Finalizing upload...')
      
      await axios.post(
        `${import.meta.env.VITE_API_URL}/files/upload/complete/${fileId}`,
        { parts },
        {
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          }
        }
      )

      updateUploadProgress(tracker.id, 100, 'Completed')
    }

    return {
      selectedFiles,
      isUploading,
      activeUploads,
      uploadResults,
      handleFileSelect,
      removeFile,
      formatFileSize,
      startUpload
    }
  }
}
</script>

<style scoped>
.file-upload {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.upload-section {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.file-input {
  display: none;
}

.select-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.select-btn:hover:not(:disabled) {
  background: #0056b3;
}

.select-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.selected-files {
  margin-bottom: 20px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.file-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.file-name {
  font-weight: 500;
}

.file-size {
  color: #6c757d;
  font-size: 12px;
}

.remove-btn {
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.upload-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.upload-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.upload-progress {
  margin-top: 20px;
}

.upload-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.upload-filename {
  font-weight: 500;
}

.upload-status {
  color: #6c757d;
  font-size: 12px;
}

.progress-bar {
  background: #e9ecef;
  border-radius: 4px;
  height: 8px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  background: #007bff;
  height: 100%;
  transition: width 0.3s;
}

.upload-details {
  font-size: 12px;
  color: #6c757d;
}

.upload-results {
  margin-top: 20px;
}

.result-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: 4px;
}

.result-status.success {
  color: #28a745;
}

.result-status.error {
  color: #dc3545;
}

.result-error {
  color: #dc3545;
  font-size: 12px;
}
</style>
