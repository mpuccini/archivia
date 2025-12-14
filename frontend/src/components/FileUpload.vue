<template>
  <a-card title="Upload File">
    <!-- File Selection -->
    <a-space direction="vertical" :size="16" style="width: 100%">
      <a-upload
        v-model:file-list="fileList"
        :before-upload="beforeUpload"
        :disabled="isUploading"
        multiple
        :show-upload-list="false"
      >
        <a-button type="primary" :disabled="isUploading" :icon="h(UploadOutlined)">
          Select Files
        </a-button>
      </a-upload>

      <!-- Selected Files -->
      <a-list
        v-if="selectedFiles.length > 0"
        size="small"
        :data-source="selectedFiles"
        bordered
      >
        <template #header>
          <strong>Selected Files:</strong>
        </template>
        <template #renderItem="{ item, index }">
          <a-list-item>
            <template #actions>
              <a-button
                type="text"
                danger
                size="small"
                @click="removeFile(index)"
                :disabled="isUploading"
              >
                ×
              </a-button>
            </template>
            <a-list-item-meta>
              <template #title>{{ item.name }}</template>
              <template #description>{{ formatFileSize(item.size) }}</template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>

      <!-- Upload Button -->
      <a-button
        v-if="selectedFiles.length > 0"
        type="primary"
        :loading="isUploading"
        @click="startUpload"
        block
        size="large"
      >
        {{ isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} File${selectedFiles.length > 1 ? 's' : ''}` }}
      </a-button>

      <!-- Upload Progress -->
      <a-card v-if="isUploading" size="small" title="Upload Progress">
        <a-space direction="vertical" :size="12" style="width: 100%">
          <div v-for="upload in activeUploads" :key="upload.id">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <a-typography-text strong>{{ upload.filename }}</a-typography-text>
              <a-typography-text type="secondary" style="font-size: 12px;">
                {{ upload.status }}
              </a-typography-text>
            </div>
            <a-progress
              :percent="Math.round(upload.progress)"
              :status="upload.progress === 100 ? 'success' : 'active'"
              :show-info="true"
            />
            <a-typography-text type="secondary" style="font-size: 12px;">
              {{ upload.speed }}
            </a-typography-text>
          </div>
        </a-space>
      </a-card>

      <!-- Upload Results -->
      <a-card v-if="uploadResults.length > 0" size="small" title="Upload Results">
        <a-space direction="vertical" :size="8" style="width: 100%">
          <a-alert
            v-for="result in uploadResults"
            :key="result.id"
            :type="result.success ? 'success' : 'error'"
            :message="result.filename"
            :description="result.success ? 'Upload successful' : result.error"
            show-icon
          />
        </a-space>
      </a-card>
    </a-space>
  </a-card>
</template>

<script>
import { ref, reactive, h } from 'vue'
import { useAuthStore } from '../stores/auth'
import { UploadOutlined } from '@ant-design/icons-vue'
import axios from 'axios'

export default {
  name: 'FileUpload',
  setup() {
    const authStore = useAuthStore()
    const selectedFiles = ref([])
    const fileList = ref([])
    const isUploading = ref(false)
    const activeUploads = reactive([])
    const uploadResults = reactive([])

    const beforeUpload = (file) => {
      selectedFiles.value = [...selectedFiles.value, file]
      return false // Prevent auto upload
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
      fileList.value = []
    }

    const uploadFile = async (file, tracker) => {
      const CHUNK_SIZE = 64 * 1024 * 1024 // 64MB chunks

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
      fileList,
      isUploading,
      activeUploads,
      uploadResults,
      beforeUpload,
      removeFile,
      formatFileSize,
      startUpload,
      h,
      UploadOutlined
    }
  }
}
</script>
