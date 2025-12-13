<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="mb-6">
      <h3 class="text-2xl font-bold text-gray-900 mb-2">Upload ECO-MiC Folder Structure</h3>
      <p class="text-gray-600">Upload a complete document folder structure with automatic file categorization</p>
    </div>

    <!-- Upload Instructions -->
    <div class="mb-6">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-sm text-blue-800">
            <p class="font-semibold mb-1">Upload ZIP Archive</p>
            <p>Compress your ECO-MiC folder structure into a ZIP archive. The folder should contain standard ECO-MiC directories (TIF.Master, JPG300, JPG150, Metadata, ICC, Logs, etc.).</p>
          </div>
        </div>
      </div>
    </div>

    <!-- File/Folder Upload Area -->
    <div
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      :class="[
        'border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer',
        isDragging
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 hover:border-gray-400 bg-gray-50'
      ]"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".zip"
        @change="handleFileSelect"
        class="hidden"
      />

      <div class="flex flex-col items-center">
        <svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>

        <p class="text-lg font-medium text-gray-900 mb-1">
          Drop ZIP file here or click to browse
        </p>
        <p class="text-sm text-gray-500">
          Supports .zip archives up to 5GB
        </p>
      </div>
    </div>

    <!-- Selected Files Display -->
    <div v-if="selectedFiles.length > 0" class="mt-6">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span class="font-semibold text-blue-900">
              ZIP Archive Selected
            </span>
          </div>
          <button
            @click="clearFiles"
            class="text-red-600 hover:text-red-700 text-sm font-medium"
          >
            Clear
          </button>
        </div>

        <div class="text-sm text-blue-800">
          <p class="font-medium">{{ selectedFiles[0].name }}</p>
          <p class="text-xs text-blue-600 mt-1">{{ formatFileSize(selectedFiles[0].size) }}</p>
        </div>
      </div>
    </div>

    <!-- Document Metadata Form -->
    <div v-if="selectedFiles.length > 0" class="mt-8 space-y-6">
      <h4 class="text-lg font-semibold text-gray-900 border-b pb-2">Document Information</h4>

      <div class="grid grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Logical ID <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.logical_id"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., DOC_2025_001"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Conservative ID
          </label>
          <input
            v-model="formData.conservative_id"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., IT-MO0172"
          />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Title <span class="text-red-500">*</span>
        </label>
        <input
          v-model="formData.title"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Document title"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          v-model="formData.description"
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Document description"
        ></textarea>
      </div>

      <div class="grid grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Archive Name</label>
          <input
            v-model="formData.archive_name"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Archive institution name"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Archive Contact</label>
          <input
            v-model="formData.archive_contact"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Contact information"
          />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
          <select
            v-model="formData.document_type"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select type...</option>
            <option value="risorsa manoscritta">Risorsa manoscritta</option>
            <option value="documento testuale">Documento testuale</option>
            <option value="risorsa a stampa">Risorsa a stampa</option>
            <option value="risorsa cartografica">Risorsa cartografica</option>
            <option value="risorsa grafica">Risorsa grafica</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Conservative ID Authority
          </label>
          <input
            v-model="formData.conservative_id_authority"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., ISIL"
          />
        </div>
      </div>
    </div>

    <!-- Upload Progress -->
    <div v-if="isUploading" class="mt-6">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-blue-900">Uploading...</span>
          <span class="text-sm text-blue-700">{{ uploadProgress }}%</span>
        </div>
        <div class="w-full bg-blue-200 rounded-full h-2">
          <div
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: uploadProgress + '%' }"
          ></div>
        </div>
        <p class="text-xs text-blue-600 mt-2">{{ uploadStatus }}</p>
      </div>
    </div>

    <!-- Upload Result -->
    <div v-if="uploadResult" class="mt-6">
      <div :class="[
        'border rounded-lg p-4',
        uploadResult.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
      ]">
        <div class="flex items-start">
          <svg
            v-if="uploadResult.success"
            class="w-5 h-5 text-green-600 mr-2 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <svg
            v-else
            class="w-5 h-5 text-red-600 mr-2 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <div class="flex-1">
            <p :class="['font-semibold', uploadResult.success ? 'text-green-900' : 'text-red-900']">
              {{ uploadResult.message }}
            </p>

            <!-- File Categorization Results -->
            <div v-if="uploadResult.success && uploadResult.categorized_files" class="mt-4">
              <p class="text-sm font-medium text-green-800 mb-2">
                Files categorized ({{ uploadResult.total_files }} total):
              </p>
              <div class="grid grid-cols-2 gap-3 text-xs">
                <div
                  v-for="(files, category) in uploadResult.categorized_files"
                  :key="category"
                  class="bg-white rounded p-2 border border-green-200"
                >
                  <div class="font-semibold text-green-900">{{ formatCategory(category) }}</div>
                  <div class="text-green-700">{{ files.length }} file(s)</div>
                  <div class="text-green-600 text-xs mt-1">
                    {{ files[0]?.file_use || '' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Error Details -->
            <div v-if="!uploadResult.success && uploadResult.error" class="mt-2">
              <p class="text-sm text-red-700">{{ uploadResult.error }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="mt-8 flex justify-end space-x-4">
      <button
        @click="$emit('cancel')"
        type="button"
        class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 font-medium transition-colors"
      >
        Cancel
      </button>
      <button
        @click="handleUpload"
        :disabled="!canUpload || isUploading"
        type="button"
        class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
      >
        {{ isUploading ? 'Uploading...' : 'Upload Document' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import axios from 'axios'

export default {
  name: 'FolderUpload',
  emits: ['cancel', 'success'],
  setup(props, { emit }) {
    const selectedFiles = ref([])
    const isDragging = ref(false)
    const fileInput = ref(null)
    const isUploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const uploadResult = ref(null)

    const formData = ref({
      logical_id: '',
      title: '',
      description: '',
      conservative_id: '',
      conservative_id_authority: '',
      archive_name: '',
      archive_contact: '',
      document_type: ''
    })

    const canUpload = computed(() => {
      return selectedFiles.value.length > 0 &&
             formData.value.logical_id.trim() !== '' &&
             formData.value.title.trim() !== ''
    })

    const triggerFileInput = () => {
      fileInput.value.click()
    }

    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      if (files.length > 0) {
        selectedFiles.value = files
        uploadResult.value = null
      }
    }

    const handleDrop = (event) => {
      isDragging.value = false
      const files = Array.from(event.dataTransfer.files)
      const zipFile = files.find(f => f.name.endsWith('.zip'))
      if (zipFile) {
        selectedFiles.value = [zipFile]
        uploadResult.value = null
      }
    }

    const clearFiles = () => {
      selectedFiles.value = []
      uploadResult.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    const formatCategory = (category) => {
      const categoryNames = {
        master: 'Master Files',
        normalized: 'Normalized',
        export_high: 'High Quality Export',
        export_low: 'Low Quality Export',
        metadata: 'Metadata',
        icc: 'ICC Profiles',
        logs: 'Logs',
        other: 'Other'
      }
      return categoryNames[category] || category
    }

    const handleUpload = async () => {
      if (!canUpload.value) return

      isUploading.value = true
      uploadProgress.value = 0
      uploadStatus.value = 'Preparing upload...'
      uploadResult.value = null

      try {
        const token = localStorage.getItem('token')
        if (!token) {
          throw new Error('Not authenticated')
        }

        const formDataToSend = new FormData()

        // ZIP file upload
        uploadStatus.value = 'Uploading ZIP archive...'
        formDataToSend.append('zip_file', selectedFiles.value[0])

        // Add metadata
        formDataToSend.append('logical_id', formData.value.logical_id)
        formDataToSend.append('title', formData.value.title)
        if (formData.value.description) formDataToSend.append('description', formData.value.description)
        if (formData.value.conservative_id) formDataToSend.append('conservative_id', formData.value.conservative_id)
        if (formData.value.conservative_id_authority) formDataToSend.append('conservative_id_authority', formData.value.conservative_id_authority)
        if (formData.value.archive_name) formDataToSend.append('archive_name', formData.value.archive_name)
        if (formData.value.archive_contact) formDataToSend.append('archive_contact', formData.value.archive_contact)
        if (formData.value.document_type) formDataToSend.append('document_type', formData.value.document_type)

        uploadStatus.value = 'Uploading to server...'

        // Upload
        const response = await axios.post(
          'http://localhost:8000/api/documents/upload-folder',
          formDataToSend,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              uploadProgress.value = percentCompleted
            }
          }
        )

        uploadProgress.value = 100
        uploadStatus.value = 'Upload complete!'

        uploadResult.value = {
          success: true,
          message: response.data.message || 'Folder uploaded successfully!',
          categorized_files: response.data.categorized_files,
          total_files: response.data.total_files,
          document_id: response.data.document_id
        }

        // Emit success event
        setTimeout(() => {
          emit('success', response.data)
        }, 2000)

      } catch (error) {
        console.error('Upload error:', error)
        uploadResult.value = {
          success: false,
          message: 'Upload failed',
          error: error.response?.data?.detail || error.message
        }
      } finally {
        isUploading.value = false
      }
    }

    return {
      selectedFiles,
      isDragging,
      fileInput,
      isUploading,
      uploadProgress,
      uploadStatus,
      uploadResult,
      formData,
      canUpload,
      triggerFileInput,
      handleFileSelect,
      handleDrop,
      clearFiles,
      formatFileSize,
      formatCategory,
      handleUpload
    }
  }
}
</script>
