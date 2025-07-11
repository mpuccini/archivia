<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content document-detail-modal" @click.stop>
      <div class="modal-header">
        <h3>{{ document.title || document.logical_id }}</h3>
        <button @click="$emit('close')" class="close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="document-detail-layout">
          <!-- Metadata Section (Left) -->
          <div class="metadata-section">
            <h4>Document Metadata</h4>
            <div class="metadata-grid">
              <div class="metadata-item">
                <label>Logical ID:</label>
                <span>{{ document.logical_id }}</span>
              </div>
              <div class="metadata-item" v-if="document.conservative_id">
                <label>Conservative ID:</label>
                <span>{{ document.conservative_id }}</span>
              </div>
              <div class="metadata-item" v-if="document.title">
                <label>Title:</label>
                <span>{{ document.title }}</span>
              </div>
              <div class="metadata-item" v-if="document.description">
                <label>Description:</label>
                <span>{{ document.description }}</span>
              </div>
              <div class="metadata-item" v-if="document.archive_name">
                <label>Archive:</label>
                <span>{{ document.archive_name }}</span>
              </div>
              <div class="metadata-item" v-if="document.document_type">
                <label>Type:</label>
                <span>{{ document.document_type }}</span>
              </div>
              <div class="metadata-item" v-if="document.total_pages">
                <label>Total Pages:</label>
                <span>{{ document.total_pages }}</span>
              </div>
              <div class="metadata-item" v-if="document.image_producer">
                <label>Image Producer:</label>
                <span>{{ document.image_producer }}</span>
              </div>
              <div class="metadata-item" v-if="document.scanner_manufacturer">
                <label>Scanner:</label>
                <span>{{ document.scanner_manufacturer }} {{ document.scanner_model }}</span>
              </div>
              <div class="metadata-item" v-if="document.license_url">
                <label>License:</label>
                <a :href="document.license_url" target="_blank">{{ document.license_url }}</a>
              </div>
              <div class="metadata-item" v-if="document.rights_statement">
                <label>Rights:</label>
                <span>{{ document.rights_statement }}</span>
              </div>
              <div class="metadata-item">
                <label>Created:</label>
                <span>{{ formatDate(document.created_at) }}</span>
              </div>
              <div class="metadata-item" v-if="document.updated_at !== document.created_at">
                <label>Updated:</label>
                <span>{{ formatDate(document.updated_at) }}</span>
              </div>
            </div>

            <!-- Files Information -->
            <h4 class="files-header">Associated Files ({{ document.document_files?.length || 0 }})</h4>
            <div class="files-list" v-if="document.document_files && document.document_files.length > 0">
              <div 
                v-for="file in document.document_files" 
                :key="file.id" 
                class="file-item"
                :class="{ active: selectedFile?.id === file.id }"
                @click="selectFile(file)"
              >
                <div class="file-info">
                  <span class="file-name">{{ file.filename }}</span>
                  <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
                </div>
                <div class="file-metadata">
                  <span v-if="file.file_use">{{ file.file_use }}</span>
                  <span v-if="file.sequence_number">Seq: {{ file.sequence_number }}</span>
                </div>
              </div>
            </div>
            <div v-else class="no-files">
              No files associated with this document
            </div>
          </div>

          <!-- Preview Section (Right) -->
          <div class="preview-section">
            <h4>File Preview</h4>
            <div v-if="selectedFile" class="preview-container">
              <div class="preview-header">
                <span class="preview-title">{{ selectedFile.filename }}</span>
                <button @click="downloadFile(selectedFile)" class="btn btn-sm btn-outline">
                  <i class="icon-download"></i> Download
                </button>
              </div>
              
              <div class="preview-content">
                <div v-if="isImageFile(selectedFile)" class="image-preview">
                  <img 
                    :src="getFilePreviewUrl(selectedFile)" 
                    :alt="selectedFile.filename"
                    @load="imageLoaded = true"
                    @error="imageError = true"
                    v-show="imageLoaded && !imageError"
                  />
                  <div v-if="!imageLoaded && !imageError" class="loading-preview">
                    Loading preview...
                  </div>
                  <div v-if="imageError" class="error-preview">
                    Preview not available
                  </div>
                </div>
                
                <div v-else class="file-info-preview">
                  <div class="file-icon">📄</div>
                  <div class="file-details">
                    <p><strong>Type:</strong> {{ selectedFile.content_type }}</p>
                    <p><strong>Size:</strong> {{ formatFileSize(selectedFile.file_size) }}</p>
                    <p v-if="selectedFile.checksum_md5"><strong>MD5:</strong> {{ selectedFile.checksum_md5 }}</p>
                    <p v-if="selectedFile.image_width && selectedFile.image_height">
                      <strong>Dimensions:</strong> {{ selectedFile.image_width }} × {{ selectedFile.image_height }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="no-preview">
              <div class="no-preview-content">
                <div class="no-preview-icon">🖼️</div>
                <p>Select a file from the left to preview</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="downloadArchive" class="btn btn-primary">
          <i class="icon-download"></i> Download Complete Archive
        </button>
        <button @click="$emit('close')" class="btn btn-secondary">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'DocumentDetailModal',
  props: {
    document: {
      type: Object,
      required: true
    }
  },
  emits: ['close'],
  setup(props) {
    const authStore = useAuthStore()
    const selectedFile = ref(null)
    const imageLoaded = ref(false)
    const imageError = ref(false)

    // Auto-select first file if available
    watch(() => props.document, (newDoc) => {
      if (newDoc?.document_files && newDoc.document_files.length > 0) {
        selectedFile.value = newDoc.document_files[0]
      }
    }, { immediate: true })

    const selectFile = (file) => {
      selectedFile.value = file
      imageLoaded.value = false
      imageError.value = false
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return 'N/A'
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      if (bytes === 0) return '0 Bytes'
      const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }

    const isImageFile = (file) => {
      if (!file.content_type) return false
      return file.content_type.startsWith('image/')
    }

    const getFilePreviewUrl = (file) => {
      // For now, return a placeholder or the file download URL
      // In a real implementation, you'd get a presigned URL from the backend
      return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/files/${file.file_id}/download`
    }

    const downloadFile = async (file) => {
      try {
        const token = authStore.token
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/files/${file.file_id}/download`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
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
        alert('Error downloading file')
      }
    }

    const downloadArchive = async () => {
      try {
        const token = authStore.token
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${props.document.id}/download/archive`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        )
        
        if (!response.ok) throw new Error('Download failed')
        
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${props.document.logical_id}_complete.zip`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } catch (error) {
        console.error('Error downloading archive:', error)
        alert('Error downloading archive')
      }
    }

    return {
      selectedFile,
      imageLoaded,
      imageError,
      selectFile,
      formatDate,
      formatFileSize,
      isImageFile,
      getFilePreviewUrl,
      downloadFile,
      downloadArchive
    }
  }
}
</script>

<style scoped>
.document-detail-modal {
  max-width: 1200px;
  width: 95vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-body {
  flex: 1;
  overflow: hidden;
  padding: 0;
}

.document-detail-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  height: 70vh;
  padding: 1.5rem;
}

.metadata-section,
.preview-section {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.metadata-section h4,
.preview-section h4 {
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e9ecef;
  color: #495057;
}

.metadata-grid {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  overflow-y: auto;
}

.metadata-item {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 0.5rem;
  align-items: start;
}

.metadata-item label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.9rem;
}

.metadata-item span,
.metadata-item a {
  color: #495057;
  word-break: break-word;
}

.metadata-item a {
  color: #007bff;
  text-decoration: none;
}

.metadata-item a:hover {
  text-decoration: underline;
}

.files-header {
  margin: 1rem 0 0.5rem 0 !important;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
  font-size: 1rem;
}

.files-list {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.file-item {
  padding: 0.75rem;
  border-bottom: 1px solid #f8f9fa;
  cursor: pointer;
  transition: background-color 0.2s;
}

.file-item:hover {
  background-color: #f8f9fa;
}

.file-item.active {
  background-color: #e3f2fd;
  border-left: 3px solid #007bff;
}

.file-item:last-child {
  border-bottom: none;
}

.file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.file-name {
  font-weight: 500;
  color: #495057;
}

.file-size {
  font-size: 0.8rem;
  color: #6c757d;
}

.file-metadata {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #6c757d;
}

.no-files {
  padding: 2rem;
  text-align: center;
  color: #6c757d;
  font-style: italic;
}

.preview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.preview-title {
  font-weight: 500;
  color: #495057;
}

.preview-content {
  flex: 1;
  overflow: hidden;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.loading-preview,
.error-preview {
  color: #6c757d;
  font-style: italic;
}

.file-info-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.file-icon {
  font-size: 3rem;
}

.file-details {
  text-align: center;
}

.file-details p {
  margin: 0.5rem 0;
  color: #495057;
}

.no-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-preview-content {
  text-align: center;
  color: #6c757d;
}

.no-preview-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

.btn-outline {
  background-color: transparent;
  color: #007bff;
  border: 1px solid #007bff;
}

.btn-outline:hover {
  background-color: #007bff;
  color: white;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .document-detail-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .document-detail-modal {
    width: 98vw;
    max-height: 95vh;
  }
}
</style>
