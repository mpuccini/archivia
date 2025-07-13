<template>
  <div class="space-y-6">
    <!-- Step 1: File Upload -->
    <div v-if="currentStep === 1">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Upload Excel File</h3>
      <p class="text-sm text-gray-600 mb-6">
        Upload an Excel file (.xlsx) with document metadata. The first row should contain column headers.
      </p>
      
      <!-- File Upload Area -->
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
          <label for="excel-upload" class="cursor-pointer">
            <span class="text-blue-600 hover:text-blue-500 font-medium">Click to upload</span>
            <span class="text-gray-500"> or drag and drop</span>
            <input
              id="excel-upload"
              type="file"
              accept=".xlsx,.xls"
              @change="handleFileSelect"
              class="sr-only"
            />
          </label>
          <p class="text-xs text-gray-500 mt-2">Excel files (.xlsx, .xls) up to 10MB</p>
        </div>
      </div>

      <!-- Selected File -->
      <div v-if="selectedFile" class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div class="flex items-center">
          <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a4 4 0 01-4-4V5a4 4 0 014-4h6l4 4v10a4 4 0 01-4 4z"></path>
          </svg>
          <div class="ml-4 flex-1">
            <p class="text-sm font-medium text-blue-900">{{ selectedFile.name }}</p>
            <p class="text-sm text-blue-700">{{ formatFileSize(selectedFile.size) }}</p>
          </div>
          <button
            @click="removeFile"
            class="ml-4 text-blue-400 hover:text-blue-600"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
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
          @click="parseExcelFile"
          :disabled="!selectedFile || isProcessing"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg v-if="isProcessing" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isProcessing ? 'Processing...' : 'Parse File' }}
        </button>
      </div>
    </div>

    <!-- Step 2: Preview and Confirm -->
    <div v-if="currentStep === 2">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Preview Documents</h3>
      <p class="text-sm text-gray-600 mb-6">
        Review the {{ parsedDocuments.length }} documents that will be created. You can edit individual fields if needed.
      </p>

      <!-- Error Messages -->
      <div v-if="parseErrors.length > 0" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <h4 class="text-sm font-medium text-red-800 mb-2">Parsing Issues:</h4>
        <ul class="text-sm text-red-700 space-y-1">
          <li v-for="error in parseErrors" :key="error">• {{ error }}</li>
        </ul>
      </div>

      <!-- Documents Preview Table -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
        <div class="overflow-x-auto max-h-96">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Row
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Logical ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Archive
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Creator
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(doc, index) in parsedDocuments" :key="index" :class="doc.hasErrors ? 'bg-red-50' : ''">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ index + 2 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  <input
                    v-model="doc.logical_id"
                    class="w-full px-2 py-1 border border-gray-300 rounded-md text-sm"
                    :class="!doc.logical_id ? 'border-red-300 bg-red-50' : ''"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <input
                    v-model="doc.title"
                    class="w-full px-2 py-1 border border-gray-300 rounded-md text-sm"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <input
                    v-model="doc.archive_name"
                    class="w-full px-2 py-1 border border-gray-300 rounded-md text-sm"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <input
                    v-model="doc.document_type"
                    class="w-full px-2 py-1 border border-gray-300 rounded-md text-sm"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <input
                    v-model="doc.creator"
                    class="w-full px-2 py-1 border border-gray-300 rounded-md text-sm"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span v-if="!doc.logical_id" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Missing ID
                  </span>
                  <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Ready
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-between pt-6">
        <button
          @click="currentStep = 1"
          class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Back
        </button>
        <button
          @click="createDocuments"
          :disabled="!canCreateDocuments || isCreating"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg v-if="isCreating" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isCreating ? 'Creating Documents...' : `Create ${validDocuments.length} Documents` }}
        </button>
      </div>
    </div>

    <!-- Step 3: Results -->
    <div v-if="currentStep === 3">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Import Results</h3>
      
      <div v-if="importResults.success.length > 0" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <h4 class="text-sm font-medium text-green-800 mb-2">Successfully Created: {{ importResults.success.length }}</h4>
        <ul class="text-sm text-green-700 space-y-1 max-h-32 overflow-y-auto">
          <li v-for="result in importResults.success" :key="result.logical_id">
            • {{ result.logical_id }} - {{ result.title || 'Untitled' }}
          </li>
        </ul>
      </div>

      <div v-if="importResults.errors.length > 0" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <h4 class="text-sm font-medium text-red-800 mb-2">Failed to Create: {{ importResults.errors.length }}</h4>
        <ul class="text-sm text-red-700 space-y-1 max-h-32 overflow-y-auto">
          <li v-for="error in importResults.errors" :key="error.logical_id">
            • {{ error.logical_id }}: {{ error.error }}
          </li>
        </ul>
      </div>

      <!-- Actions -->
      <div class="flex justify-end pt-6">
        <button
          @click="$emit('import-complete')"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Done
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import * as XLSX from 'xlsx'

export default {
  name: 'ExcelBatchImport',
  emits: ['import-complete', 'cancel'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    const currentStep = ref(1)
    const selectedFile = ref(null)
    const isProcessing = ref(false)
    const isCreating = ref(false)
    const parsedDocuments = ref([])
    const parseErrors = ref([])
    const importResults = ref({ success: [], errors: [] })

    const validDocuments = computed(() => {
      return parsedDocuments.value.filter(doc => doc.logical_id && doc.logical_id.trim())
    })

    const canCreateDocuments = computed(() => {
      return validDocuments.value.length > 0
    })

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const handleDrop = (e) => {
      e.preventDefault()
      const files = e.dataTransfer.files
      if (files.length > 0) {
        handleFile(files[0])
      }
    }

    const handleFileSelect = (e) => {
      const files = e.target.files
      if (files.length > 0) {
        handleFile(files[0])
      }
    }

    const handleFile = (file) => {
      if (!file.name.match(/\.(xlsx|xls)$/i)) {
        alert('Please select an Excel file (.xlsx or .xls)')
        return
      }
      
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB')
        return
      }

      selectedFile.value = file
    }

    const removeFile = () => {
      selectedFile.value = null
    }

    const parseExcelFile = async () => {
      if (!selectedFile.value) return

      isProcessing.value = true
      parseErrors.value = []

      try {
        const buffer = await selectedFile.value.arrayBuffer()
        const workbook = XLSX.read(buffer, { type: 'buffer' })
        
        // Get the first worksheet
        const sheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[sheetName]
        
        // Convert to JSON with header row
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
        
        if (jsonData.length < 2) {
          throw new Error('Excel file must contain at least a header row and one data row')
        }

        const headers = jsonData[0]
        const rows = jsonData.slice(1)

        // Map common field variations to our schema
        const fieldMapping = {
          'logical_id': ['logical_id', 'logicalid', 'id', 'document_id'],
          'title': ['title', 'dc:title', 'mods:title'],
          'archive_name': ['archive_name', 'archive', 'collection', 'dc:source'],
          'document_type': ['document_type', 'type', 'dc:type', 'mods:genre'],
          'creator': ['creator', 'dc:creator', 'mods:name'],
          'subject': ['subject', 'dc:subject', 'mods:subject'],
          'description': ['description', 'dc:description', 'mods:abstract'],
          'publisher': ['publisher', 'dc:publisher', 'mods:publisher'],
          'date_created': ['date_created', 'date', 'dc:date', 'mods:dateCreated'],
          'language': ['language', 'dc:language', 'mods:language'],
          'format': ['format', 'dc:format', 'mods:physicalDescription'],
          'identifier': ['identifier', 'dc:identifier', 'mods:identifier'],
          'rights': ['rights', 'dc:rights', 'mods:accessCondition'],
          'coverage': ['coverage', 'dc:coverage', 'mods:subject'],
          'total_pages': ['total_pages', 'pages', 'page_count'],
          'notes': ['notes', 'note', 'dc:relation', 'mods:note']
        }

        // Create header mapping
        const headerMap = {}
        headers.forEach((header, index) => {
          const normalizedHeader = header.toLowerCase().trim()
          for (const [field, variations] of Object.entries(fieldMapping)) {
            if (variations.some(variation => normalizedHeader.includes(variation))) {
              headerMap[index] = field
              break
            }
          }
        })

        // Parse rows
        const documents = []
        rows.forEach((row, rowIndex) => {
          const doc = {}
          let hasData = false

          row.forEach((cell, cellIndex) => {
            if (headerMap[cellIndex] && cell !== null && cell !== undefined && cell !== '') {
              doc[headerMap[cellIndex]] = String(cell).trim()
              hasData = true
            }
          })

          if (hasData) {
            // Validate required fields
            if (!doc.logical_id) {
              parseErrors.value.push(`Row ${rowIndex + 2}: Missing logical_id`)
              doc.hasErrors = true
            }

            // Convert numeric fields
            if (doc.total_pages) {
              const pages = parseInt(doc.total_pages)
              if (!isNaN(pages)) {
                doc.total_pages = pages
              }
            }

            documents.push(doc)
          }
        })

        if (documents.length === 0) {
          throw new Error('No valid document data found in the Excel file')
        }

        parsedDocuments.value = documents
        currentStep.value = 2

      } catch (error) {
        console.error('Error parsing Excel file:', error)
        alert('Error parsing Excel file: ' + error.message)
      } finally {
        isProcessing.value = false
      }
    }

    const createDocuments = async () => {
      if (!canCreateDocuments.value) return

      isCreating.value = true
      importResults.value = { success: [], errors: [] }

      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/documents/batch`, {
          documents: validDocuments.value
        }, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          }
        })

        importResults.value = response.data
        currentStep.value = 3

      } catch (error) {
        console.error('Error creating documents:', error)
        alert('Error creating documents: ' + (error.response?.data?.detail || error.message))
      } finally {
        isCreating.value = false
      }
    }

    return {
      currentStep,
      selectedFile,
      isProcessing,
      isCreating,
      parsedDocuments,
      parseErrors,
      importResults,
      validDocuments,
      canCreateDocuments,
      formatFileSize,
      handleDrop,
      handleFileSelect,
      removeFile,
      parseExcelFile,
      createDocuments
    }
  }
}
</script>
