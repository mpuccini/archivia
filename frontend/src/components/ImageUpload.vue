<template>
  <div class="space-y-6">
    <!-- Mode Selection -->
    <div v-if="!document" class="mb-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Upload Mode</h3>
      <div class="grid grid-cols-2 gap-4">
        <button
          @click="uploadMode = 'single'"
          :class="[
            'p-4 border-2 rounded-lg text-left transition-colors',
            uploadMode === 'single'
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-gray-300 hover:border-gray-400'
          ]"
        >
          <div class="flex items-center">
            <svg class="h-8 w-8 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            <div>
              <h4 class="font-medium">Single Document</h4>
              <p class="text-sm text-gray-500">Upload one image for a specific document</p>
            </div>
          </div>
        </button>
        
        <button
          @click="uploadMode = 'batch'"
          :class="[
            'p-4 border-2 rounded-lg text-left transition-colors',
            uploadMode === 'batch'
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-gray-300 hover:border-gray-400'
          ]"
        >
          <div class="flex items-center">
            <svg class="h-8 w-8 text-purple-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
            </svg>
            <div>
              <h4 class="font-medium">Batch Upload</h4>
              <p class="text-sm text-gray-500">Upload multiple images, auto-match by filename</p>
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- Single Document Mode -->
    <div v-if="uploadMode === 'single'">
      <!-- Document Selection (if not pre-selected) -->
      <div v-if="!document" class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">Select Document</label>
        <select
          v-model="selectedDocumentId"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Choose a document...</option>
          <option v-for="doc in availableDocuments" :key="doc.id" :value="doc.id">
            {{ doc.logical_id }} - {{ doc.title || 'Untitled' }}
          </option>
        </select>
      </div>

      <!-- File Upload for Single -->
      <div v-if="document || selectedDocumentId">
        <h3 class="text-lg font-medium text-gray-900 mb-4">
          Upload Image for {{ getDocumentLogicalId() }}
        </h3>
        
        <div
          @drop="handleSingleDrop"
          @dragover.prevent
          @dragenter.prevent
          class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors"
        >
          <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <div class="mt-4">
            <label for="single-image-upload" class="cursor-pointer">
              <span class="text-blue-600 hover:text-blue-500 font-medium">Click to upload</span>
              <span class="text-gray-500"> or drag and drop</span>
              <input
                id="single-image-upload"
                type="file"
                accept=".jpg,.jpeg,.png,.tiff,.tif,.pdf"
                @change="handleSingleFileSelect"
                class="sr-only"
              />
            </label>
            <p class="text-xs text-gray-500 mt-2">Images: JPG, PNG, TIFF, PDF up to 50MB</p>
          </div>
        </div>

        <!-- Selected Single File -->
        <div v-if="singleFile" class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div class="flex items-center">
            <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            <div class="ml-4 flex-1">
              <p class="text-sm font-medium text-blue-900">{{ singleFile.name }}</p>
              <p class="text-sm text-blue-700">{{ formatFileSize(singleFile.size) }}</p>
            </div>
            <button
              @click="singleFile = null"
              class="ml-4 text-blue-400 hover:text-blue-600"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Batch Mode -->
    <div v-if="uploadMode === 'batch'">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Batch Upload Images</h3>
      <p class="text-sm text-gray-600 mb-6">
        Upload multiple images. They will be automatically matched to documents based on filename = logical_id.
        For example, "DOC001.jpg" will be matched to document with logical_id "DOC001".
      </p>
      
      <div
        @drop="handleBatchDrop"
        @dragover.prevent
        @dragenter.prevent
        class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors"
      >
        <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <div class="mt-4">
          <label for="batch-image-upload" class="cursor-pointer">
            <span class="text-blue-600 hover:text-blue-500 font-medium">Click to upload</span>
            <span class="text-gray-500"> or drag and drop</span>
            <input
              id="batch-image-upload"
              type="file"
              accept=".jpg,.jpeg,.png,.tiff,.tif,.pdf"
              multiple
              @change="handleBatchFileSelect"
              class="sr-only"
            />
          </label>
          <p class="text-xs text-gray-500 mt-2">Images: JPG, PNG, TIFF, PDF up to 50MB each</p>
        </div>
      </div>

      <!-- Batch Files List -->
      <div v-if="batchFiles.length > 0" class="mt-6">
        <h4 class="text-sm font-medium text-gray-900 mb-4">Selected Files ({{ batchFiles.length }})</h4>
        <div class="bg-white shadow overflow-hidden sm:rounded-lg">
          <div class="max-h-60 overflow-y-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50 sticky top-0">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Filename
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Match Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(file, index) in batchFiles" :key="index">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {{ file.name }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatFileSize(file.size) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span 
                      :class="[
                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                        getMatchStatus(file).found 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      ]"
                    >
                      {{ getMatchStatus(file).status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button
                      @click="removeBatchFile(index)"
                      class="text-red-400 hover:text-red-600"
                    >
                      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Conflict Resolution -->
    <div v-if="conflicts.length > 0" class="mt-6">
      <h4 class="text-sm font-medium text-red-800 mb-4">Resolve Conflicts</h4>
      <div class="space-y-4">
        <div v-for="conflict in conflicts" :key="conflict.logical_id" class="p-4 bg-red-50 border border-red-200 rounded-lg">
          <h5 class="font-medium text-red-900 mb-2">{{ conflict.logical_id }}</h5>
          <p class="text-sm text-red-700 mb-3">{{ conflict.message }}</p>
          <div class="space-y-2">
            <label class="flex items-center">
              <input
                type="radio"
                :name="`conflict_${conflict.logical_id}`"
                value="keep"
                v-model="conflict.resolution"
                class="mr-2"
              />
              <span class="text-sm">Keep existing image</span>
            </label>
            <label class="flex items-center">
              <input
                type="radio"
                :name="`conflict_${conflict.logical_id}`"
                value="replace"
                v-model="conflict.resolution"
                class="mr-2"
              />
              <span class="text-sm">Replace with new image</span>
            </label>
            <label v-if="conflict.type === 'multiple'" class="flex items-center">
              <input
                type="radio"
                :name="`conflict_${conflict.logical_id}`"
                value="choose"
                v-model="conflict.resolution"
                class="mr-2"
              />
              <span class="text-sm">Let me choose which file to use</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-between pt-6">
      <button
        @click="$emit('cancel')"
        class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Cancel
      </button>
      <button
        @click="uploadImages"
        :disabled="!canUpload || isUploading"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg v-if="isUploading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isUploading ? 'Uploading...' : getUploadButtonText() }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

export default {
  name: 'ImageUpload',
  props: {
    document: {
      type: Object,
      default: null
    }
  },
  emits: ['upload-complete', 'cancel'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    
    // Mode and state
    const uploadMode = ref(props.document ? 'single' : 'batch')
    const isUploading = ref(false)
    
    // Single mode
    const selectedDocumentId = ref(props.document?.id || '')
    const singleFile = ref(null)
    const availableDocuments = ref([])
    
    // Batch mode
    const batchFiles = ref([])
    const conflicts = ref([])

    const canUpload = computed(() => {
      if (uploadMode.value === 'single') {
        return singleFile.value && (props.document || selectedDocumentId.value)
      } else {
        return batchFiles.value.length > 0 && conflicts.value.every(c => c.resolution)
      }
    })

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const getDocumentLogicalId = () => {
      if (props.document) return props.document.logical_id
      const doc = availableDocuments.value.find(d => d.id === selectedDocumentId.value)
      return doc?.logical_id || ''
    }

    const getUploadButtonText = () => {
      if (uploadMode.value === 'single') {
        return 'Upload Image'
      } else {
        return `Upload ${batchFiles.value.length} Images`
      }
    }

    const isValidImageFile = (file) => {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'application/pdf']
      const validExtensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.pdf']
      
      return validTypes.includes(file.type) || 
             validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))
    }

    const extractLogicalIdFromFilename = (filename) => {
      // Remove file extension and return the base name
      return filename.replace(/\.[^/.]+$/, '')
    }

    const getMatchStatus = (file) => {
      const logicalId = extractLogicalIdFromFilename(file.name)
      const document = availableDocuments.value.find(d => d.logical_id === logicalId)
      
      if (document) {
        return { found: true, status: `Matches ${logicalId}`, document }
      } else {
        return { found: false, status: 'Will create new document', document: null }
      }
    }

    const handleSingleDrop = (e) => {
      e.preventDefault()
      const files = e.dataTransfer.files
      if (files.length > 0) {
        handleSingleFile(files[0])
      }
    }

    const handleSingleFileSelect = (e) => {
      const files = e.target.files
      if (files.length > 0) {
        handleSingleFile(files[0])
      }
    }

    const handleSingleFile = (file) => {
      if (!isValidImageFile(file)) {
        alert('Please select a valid image file (JPG, PNG, TIFF, PDF)')
        return
      }
      
      if (file.size > 50 * 1024 * 1024) {
        alert('File size must be less than 50MB')
        return
      }

      singleFile.value = file
    }

    const handleBatchDrop = (e) => {
      e.preventDefault()
      const files = Array.from(e.dataTransfer.files)
      handleBatchFiles(files)
    }

    const handleBatchFileSelect = (e) => {
      const files = Array.from(e.target.files)
      handleBatchFiles(files)
    }

    const handleBatchFiles = (files) => {
      const validFiles = files.filter(file => {
        if (!isValidImageFile(file)) {
          console.warn(`Skipping invalid file: ${file.name}`)
          return false
        }
        if (file.size > 50 * 1024 * 1024) {
          console.warn(`Skipping large file: ${file.name}`)
          return false
        }
        return true
      })

      // Check for duplicates
      const existingNames = batchFiles.value.map(f => f.name)
      const newFiles = validFiles.filter(f => !existingNames.includes(f.name))
      
      batchFiles.value.push(...newFiles)
      
      // Check for conflicts
      checkForConflicts()
    }

    const removeBatchFile = (index) => {
      batchFiles.value.splice(index, 1)
      checkForConflicts()
    }

    const checkForConflicts = () => {
      conflicts.value = []
      
      // Group files by logical_id
      const fileGroups = {}
      batchFiles.value.forEach(file => {
        const logicalId = extractLogicalIdFromFilename(file.name)
        if (!fileGroups[logicalId]) {
          fileGroups[logicalId] = []
        }
        fileGroups[logicalId].push(file)
      })

      // Check for multiple files with same logical_id
      Object.entries(fileGroups).forEach(([logicalId, files]) => {
        if (files.length > 1) {
          conflicts.value.push({
            logical_id: logicalId,
            type: 'multiple',
            message: `Multiple files found for ${logicalId}: ${files.map(f => f.name).join(', ')}`,
            resolution: 'choose',
            files
          })
        }
      })
    }

    const loadAvailableDocuments = async () => {
      if (props.document) return // No need to load if document is pre-selected

      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents`, {
          params: { size: 1000 }, // Get all documents
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        availableDocuments.value = response.data.documents || response.data.items || response.data
      } catch (error) {
        console.error('Error loading documents:', error)
      }
    }

    const uploadImages = async () => {
      if (!canUpload.value) return

      isUploading.value = true

      try {
        if (uploadMode.value === 'single') {
          await uploadSingleImage()
        } else {
          await uploadBatchImages()
        }
        
        emit('upload-complete')
      } catch (error) {
        console.error('Error uploading images:', error)
        alert('Error uploading images: ' + (error.response?.data?.detail || error.message))
      } finally {
        isUploading.value = false
      }
    }

    const uploadSingleImage = async () => {
      const formData = new FormData()
      formData.append('file', singleFile.value)
      
      const documentId = props.document?.id || selectedDocumentId.value
      
      await axios.post(`${import.meta.env.VITE_API_URL}/api/documents/${documentId}/images`, formData, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    const uploadBatchImages = async () => {
      const formData = new FormData()
      
      batchFiles.value.forEach(file => {
        formData.append('files', file)
      })

      // Add conflict resolutions
      conflicts.value.forEach(conflict => {
        formData.append(`conflict_${conflict.logical_id}`, conflict.resolution)
      })

      await axios.post(`${import.meta.env.VITE_API_URL}/api/documents/images/batch`, formData, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    onMounted(() => {
      loadAvailableDocuments()
    })

    return {
      uploadMode,
      isUploading,
      selectedDocumentId,
      singleFile,
      availableDocuments,
      batchFiles,
      conflicts,
      canUpload,
      formatFileSize,
      getDocumentLogicalId,
      getUploadButtonText,
      getMatchStatus,
      handleSingleDrop,
      handleSingleFileSelect,
      handleBatchDrop,
      handleBatchFileSelect,
      removeBatchFile,
      uploadImages
    }
  }
}
</script>
