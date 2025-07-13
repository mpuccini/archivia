<template>
  <div class="space-y-6">
    <div>
      <h3 class="text-lg font-medium text-gray-900 mb-4">Batch Upload Images</h3>
      <p class="text-sm text-gray-600 mb-6">
        Upload multiple images. They will be automatically matched to documents based on filename = logical_id.
        For example, "DOC001.jpg" will be matched to document with logical_id "DOC001".
        If no matching document is found, a new document will be created automatically.
      </p>
      
      <div
        @drop="handleDrop"
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
              @change="handleFileSelect"
              class="sr-only"
            />
          </label>
          <p class="text-xs text-gray-500 mt-2">Images: JPG, PNG, TIFF, PDF up to 50MB each</p>
        </div>
      </div>

      <!-- Files List -->
      <div v-if="files.length > 0" class="mt-6">
        <h4 class="text-sm font-medium text-gray-900 mb-4">Selected Files ({{ files.length }})</h4>
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
                <tr v-for="(file, index) in files" :key="index">
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
                      @click="removeFile(index)"
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
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg v-if="isUploading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isUploading ? 'Uploading...' : `Upload ${files.length} Images` }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

export default {
  name: 'BatchImageUpload',
  emits: ['upload-complete', 'cancel'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    
    const isUploading = ref(false)
    const files = ref([])
    const conflicts = ref([])
    const availableDocuments = ref([])

    const canUpload = computed(() => {
      return files.value.length > 0 && conflicts.value.every(c => c.resolution)
    })

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const isValidImageFile = (file) => {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'application/pdf']
      const validExtensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.pdf']
      
      return validTypes.includes(file.content_type) || 
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

    const handleDrop = (e) => {
      e.preventDefault()
      const droppedFiles = Array.from(e.dataTransfer.files)
      handleFiles(droppedFiles)
    }

    const handleFileSelect = (e) => {
      const selectedFiles = Array.from(e.target.files)
      handleFiles(selectedFiles)
    }

    const handleFiles = (newFiles) => {
      const validFiles = newFiles.filter(file => {
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
      const existingNames = files.value.map(f => f.name)
      const uniqueFiles = validFiles.filter(f => !existingNames.includes(f.name))
      
      files.value.push(...uniqueFiles)
      
      // Check for conflicts
      checkForConflicts()
    }

    const removeFile = (index) => {
      files.value.splice(index, 1)
      checkForConflicts()
    }

    const checkForConflicts = () => {
      conflicts.value = []
      
      // Group files by logical_id
      const fileGroups = {}
      files.value.forEach(file => {
        const logicalId = extractLogicalIdFromFilename(file.name)
        if (!fileGroups[logicalId]) {
          fileGroups[logicalId] = []
        }
        fileGroups[logicalId].push(file)
      })

      // Check for multiple files with same logical_id
      Object.entries(fileGroups).forEach(([logicalId, groupFiles]) => {
        if (groupFiles.length > 1) {
          conflicts.value.push({
            logical_id: logicalId,
            type: 'multiple',
            message: `Multiple files found for ${logicalId}: ${groupFiles.map(f => f.name).join(', ')}`,
            resolution: 'choose',
            files: groupFiles
          })
        }
      })
    }

    const loadAvailableDocuments = async () => {
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
        const formData = new FormData()
        
        files.value.forEach(file => {
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
        
        emit('upload-complete')
      } catch (error) {
        console.error('Error uploading images:', error)
        alert('Error uploading images: ' + (error.response?.data?.detail || error.message))
      } finally {
        isUploading.value = false
      }
    }

    onMounted(() => {
      loadAvailableDocuments()
    })

    return {
      isUploading,
      files,
      conflicts,
      canUpload,
      formatFileSize,
      getMatchStatus,
      handleDrop,
      handleFileSelect,
      removeFile,
      uploadImages
    }
  }
}
</script>
