<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content document-detail-modal" @click.stop>
      <div class="modal-header">
        <h3>{{ document.title || document.logical_id }}</h3>
        <div class="modal-actions">
          <button 
            v-if="!isEditing" 
            @click="startEdit" 
            class="btn btn-sm btn-primary edit-btn"
          >
            Edit
          </button>
          <button 
            v-if="isEditing" 
            @click="saveChanges" 
            class="btn btn-sm btn-primary save-btn"
            :disabled="saving"
          >
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
          <button 
            v-if="isEditing" 
            @click="cancelEdit" 
            class="btn btn-sm btn-secondary cancel-btn"
            :disabled="saving"
          >
            Cancel
          </button>
          <button @click="$emit('close')" class="btn btn-sm btn-secondary">×</button>
        </div>
      </div>

      <div class="modal-body">
        <div class="document-detail-layout">
          <div class="metadata-panel">
            <h4>Document Metadata</h4>
            
            <!-- Display mode -->
            <div v-if="!isEditing" class="metadata-display">
              <div class="metadata-item">
                <label>Logical ID:</label>
                <span>{{ document.logical_id }}</span>
              </div>
              <div class="metadata-item" v-if="document.conservative_id">
                <label>Conservative ID:</label>
                <span>{{ document.conservative_id }}</span>
              </div>
              <div class="metadata-item" v-if="document.conservative_id_authority">
                <label>Conservative ID Authority:</label>
                <span>{{ document.conservative_id_authority }}</span>
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
                <label>Archive Name:</label>
                <span>{{ document.archive_name }}</span>
              </div>
              <div class="metadata-item" v-if="document.archive_contact">
                <label>Archive Contact:</label>
                <span>{{ document.archive_contact }}</span>
              </div>
              <div class="metadata-item" v-if="document.document_type">
                <label>Document Type:</label>
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
                <label>Scanner Manufacturer:</label>
                <span>{{ document.scanner_manufacturer }}</span>
              </div>
              <div class="metadata-item" v-if="document.scanner_model">
                <label>Scanner Model:</label>
                <span>{{ document.scanner_model }}</span>
              </div>
              <div class="metadata-item" v-if="document.license_url">
                <label>License URL:</label>
                <a :href="document.license_url" target="_blank">{{ document.license_url }}</a>
              </div>
              <div class="metadata-item" v-if="document.rights_statement">
                <label>Rights Statement:</label>
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

            <!-- Edit form -->
            <div v-else class="metadata-form">
              <div class="form-section">
                <h5>Basic Information</h5>
                <div class="form-group">
                  <label for="edit-logical-id">Logical ID:</label>
                  <input 
                    type="text" 
                    id="edit-logical-id"
                    v-model="editForm.logical_id"
                    placeholder="Logical identifier"
                  />
                </div>
                <div class="form-group">
                  <label for="edit-title">Title:</label>
                  <input 
                    type="text" 
                    id="edit-title"
                    v-model="editForm.title"
                    placeholder="Document title"
                  />
                </div>
                <div class="form-group">
                  <label for="edit-description">Description:</label>
                  <textarea 
                    id="edit-description"
                    v-model="editForm.description"
                    placeholder="Document description"
                    rows="3"
                  ></textarea>
                </div>
              </div>

              <div class="form-section">
                <h5>Archive Information</h5>
                <div class="form-group">
                  <label for="edit-archive-name">Archive Name:</label>
                  <input 
                    type="text" 
                    id="edit-archive-name"
                    v-model="editForm.archive_name"
                    placeholder="e.g., Archivio di stato di Modena"
                  />
                </div>
                <div class="form-group">
                  <label for="edit-archive-contact">Archive Contact:</label>
                  <input 
                    type="email" 
                    id="edit-archive-contact"
                    v-model="editForm.archive_contact"
                    placeholder="e.g., as-mo@cultura.gov.it"
                  />
                </div>
                <div class="form-group">
                  <label for="edit-conservative-id">Conservative ID:</label>
                  <input 
                    type="text" 
                    id="edit-conservative-id"
                    v-model="editForm.conservative_id"
                    placeholder="e.g., IT-MO0172"
                  />
                </div>
                <div class="form-group">
                  <label for="edit-conservative-id-authority">Conservative ID Authority:</label>
                  <input 
                    type="text" 
                    id="edit-conservative-id-authority"
                    v-model="editForm.conservative_id_authority"
                    placeholder="e.g., ICCU"
                  />
                </div>
              </div>

              <div class="form-section">
                <h5>Rights & Licensing</h5>
                <div class="form-group">
                  <label for="edit-license-url">License URL:</label>
                  <input 
                    type="url" 
                    id="edit-license-url"
                    v-model="editForm.license_url"
                    placeholder="e.g., https://creativecommons.org/licenses/by/4.0/"
                  />
                </div>
                <div class="form-group">
                  <label for="edit-rights-statement">Rights Statement:</label>
                  <textarea 
                    id="edit-rights-statement"
                    v-model="editForm.rights_statement"
                    placeholder="Rights and usage information"
                    rows="2"
                  ></textarea>
                </div>
              </div>

              <div class="form-section">
                <h5>Technical Information</h5>
                <div class="form-group">
                  <label for="edit-image-producer">Image Producer:</label>
                  <input 
                    type="text" 
                    id="edit-image-producer"
                    v-model="editForm.image_producer"
                    placeholder="e.g., Archivio di stato di Modena"
                  />
                </div>
                <div class="form-group">
                  <label for="edit-scanner-manufacturer">Scanner Manufacturer:</label>
                  <input 
                    type="text" 
                    id="edit-scanner-manufacturer"
                    v-model="editForm.scanner_manufacturer"
                    placeholder="e.g., Zeutschel"
                  />
                </div>
                <div class="form-group">
                  <label for="edit-scanner-model">Scanner Model:</label>
                  <input 
                    type="text" 
                    id="edit-scanner-model"
                    v-model="editForm.scanner_model"
                    placeholder="e.g., OS 15000"
                  />
                </div>
                <div class="form-group">
                  <label for="edit-document-type">Document Type:</label>
                  <select 
                    id="edit-document-type"
                    v-model="editForm.document_type"
                  >
                    <option value="">Select a type</option>
                    <option value="manuscript">Manuscript</option>
                    <option value="book">Book</option>
                    <option value="map">Map</option>
                    <option value="photograph">Photograph</option>
                    <option value="letter">Letter</option>
                    <option value="document">Document</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="edit-total-pages">Total Pages:</label>
                  <input 
                    type="number" 
                    id="edit-total-pages"
                    v-model.number="editForm.total_pages"
                    placeholder="Number of pages"
                    min="1"
                  />
                </div>
              </div>
            </div>
          </div>

          <div class="files-panel">
            <h4>Associated Files ({{ document.document_files?.length || 0 }})</h4>
            
            <div v-if="document.document_files && document.document_files.length > 0" class="files-section">
              <div class="file-list">
                <div 
                  v-for="file in document.document_files" 
                  :key="file.file_id"
                  class="file-item"
                  :class="{ 'selected': selectedFile && selectedFile.file_id === file.file_id }"
                  @click="selectFile(file)"
                >
                  <div class="file-info">
                    <div class="file-name">{{ file.filename }}</div>
                    <div class="file-meta">
                      <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
                      <span class="file-type">{{ file.content_type }}</span>
                    </div>
                  </div>
                  <button 
                    @click.stop="downloadFile(file)" 
                    class="btn btn-sm btn-outline-primary download-btn"
                    title="Download file"
                  >
                    ⬇
                  </button>
                </div>
              </div>
            </div>
            
            <div v-else class="no-files">
              <p>No files associated with this document.</p>
            </div>

            <div v-if="selectedFile" class="file-preview">
              <h5>File Preview: {{ selectedFile.filename }}</h5>
              <div class="preview-content">
                <div v-if="isImageFile(selectedFile)" class="image-preview">
                  <img 
                    :src="imageDataUrl" 
                    :alt="selectedFile.filename"
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
import { ref, reactive, watch, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

export default {
  name: 'DocumentDetailModal',
  props: {
    document: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'documentUpdated'],
  setup(props, { emit }) {
    console.log('DocumentDetailModal: Component setup called with document:', props.document)
    console.log('DocumentDetailModal: Document files:', props.document?.document_files)
    const authStore = useAuthStore()
    const selectedFile = ref(null)
    const imageLoaded = ref(false)
    const imageError = ref(false)
    const imageDataUrl = ref('')
    
    // Edit state
    const isEditing = ref(false)
    const saving = ref(false)
    const editForm = reactive({
      logical_id: '',
      title: '',
      description: '',
      conservative_id: '',
      conservative_id_authority: '',
      archive_name: '',
      archive_contact: '',
      license_url: '',
      rights_statement: '',
      image_producer: '',
      scanner_manufacturer: '',
      scanner_model: '',
      document_type: '',
      total_pages: null
    })

    // Auto-select first file when component mounts
    onMounted(() => {
      console.log('DocumentDetailModal: Component mounted, checking for files to auto-select')
      if (props.document?.document_files && props.document.document_files.length > 0) {
        console.log('DocumentDetailModal: Auto-selecting first file in onMounted:', props.document.document_files[0])
        selectFile(props.document.document_files[0])
      } else {
        console.log('DocumentDetailModal: No files to auto-select in onMounted')
      }
    })

    // Auto-select first file if available (watch for changes)
    watch(() => props.document, (newDoc) => {
      console.log('DocumentDetailModal: Document changed:', newDoc)
      console.log('DocumentDetailModal: Document files in watch:', newDoc?.document_files)
      if (newDoc?.document_files && newDoc.document_files.length > 0) {
        console.log('DocumentDetailModal: Auto-selecting first file:', newDoc.document_files[0])
        selectFile(newDoc.document_files[0])
      } else {
        console.log('DocumentDetailModal: No files to auto-select')
        selectedFile.value = null
      }
    }, { immediate: true })

    const selectFile = (file) => {
      console.log('DocumentDetailModal: Selecting file:', file)
      selectedFile.value = file
      imageLoaded.value = false
      imageError.value = false
      imageDataUrl.value = ''
      
      // Load image data if it's an image file
      if (isImageFile(file)) {
        console.log('DocumentDetailModal: File is an image, loading data')
        loadImageData(file)
      } else {
        console.log('DocumentDetailModal: File is not an image:', file.content_type)
      }
    }

    const loadImageData = async (file) => {
      console.log('Loading image data for file:', file)
      try {
        const token = authStore.token
        const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/files/${file.file_id}/stream`
        console.log('Fetching from URL:', url)
        console.log('Using token:', token ? 'present' : 'missing')
        
        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        console.log('Response status:', response.status)
        console.log('Response headers:', Object.fromEntries(response.headers.entries()))
        
        if (!response.ok) {
          console.error('Response not OK:', response.status, response.statusText)
          throw new Error(`Failed to load image: ${response.status} ${response.statusText}`)
        }
        
        console.log('Response OK, creating blob URL')
        const blob = await response.blob()
        console.log('Blob created, size:', blob.size, 'type:', blob.type)
        const dataUrl = URL.createObjectURL(blob)
        console.log('Created blob URL:', dataUrl)
        imageDataUrl.value = dataUrl
        imageLoaded.value = true
        console.log('Image loading complete')
      } catch (error) {
        console.error('Error loading image:', error)
        imageError.value = true
      }
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
      let i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
      i = Math.min(i, sizes.length - 1) // Ensure i doesn't exceed array bounds
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }

    const isImageFile = (file) => {
      if (!file.content_type) return false
      return file.content_type.startsWith('image/')
    }

    const downloadFile = async (file) => {
      try {
        const token = authStore.token
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/files/${file.file_id}/stream`,
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

    // Edit functions
    const startEdit = () => {
      isEditing.value = true
      // Initialize form with current document data
      Object.keys(editForm).forEach(key => {
        editForm[key] = props.document[key] || (key === 'total_pages' ? null : '')
      })
    }

    const cancelEdit = () => {
      isEditing.value = false
      saving.value = false
    }

    const saveChanges = async () => {
      if (saving.value) return
      
      saving.value = true
      try {
        const token = authStore.token
        const response = await axios.put(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${props.document.id}`,
          editForm,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        )

        if (response.status === 200) {
          // Update the document object with new data
          Object.assign(props.document, response.data)
          isEditing.value = false
          emit('documentUpdated', response.data)
          console.log('Document updated successfully')
        }
      } catch (error) {
        console.error('Error updating document:', error)
        const errorMessage = error.response?.data?.detail || 'Failed to update document'
        alert(`Error: ${errorMessage}`)
      } finally {
        saving.value = false
      }
    }

    return {
      selectedFile,
      imageLoaded,
      imageError,
      imageDataUrl,
      isEditing,
      saving,
      editForm,
      selectFile,
      loadImageData,
      formatDate,
      formatFileSize,
      isImageFile,
      downloadFile,
      downloadArchive,
      startEdit,
      cancelEdit,
      saveChanges
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.document-detail-modal {
  width: 90vw;
  max-width: 1200px;
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.modal-body {
  flex: 1;
  overflow: hidden;
}

.document-detail-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  height: 60vh;
  min-height: 500px;
}

.metadata-panel, .files-panel {
  padding: 1rem;
  overflow-y: auto;
}

.metadata-panel {
  border-right: 1px solid #eee;
  background: #fafafa;
}

.files-panel {
  background: white;
}

.metadata-panel h4, .files-panel h4 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #333;
}

.metadata-display .metadata-item {
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.metadata-item label {
  font-weight: 600;
  color: #555;
  display: block;
  margin-bottom: 0.25rem;
}

.metadata-item span, .metadata-item a {
  color: #333;
  word-break: break-word;
}

.metadata-item a {
  color: #007bff;
  text-decoration: none;
}

.metadata-item a:hover {
  text-decoration: underline;
}

.file-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 1rem;
  border: 1px solid #eee;
  border-radius: 4px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.file-item:last-child {
  border-bottom: none;
}

.file-item:hover {
  background-color: #f8f9fa;
}

.file-item.selected {
  background-color: #e3f2fd;
  border-left: 3px solid #2196f3;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 0.25rem;
}

.file-meta {
  font-size: 0.875rem;
  color: #666;
}

.file-meta span {
  margin-right: 1rem;
}

.download-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.file-preview {
  border: 1px solid #eee;
  border-radius: 4px;
  overflow: hidden;
}

.file-preview h5 {
  margin: 0;
  padding: 0.75rem;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  font-size: 1rem;
}

.preview-content {
  padding: 1rem;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading-preview, .error-preview {
  padding: 2rem;
  color: #666;
  font-style: italic;
}

.file-info-preview {
  text-align: left;
}

.file-icon {
  font-size: 3rem;
  text-align: center;
  margin-bottom: 1rem;
}

.file-details p {
  margin: 0.5rem 0;
}

.no-files, .no-preview {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.no-preview-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.no-preview-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
}

.btn-outline-primary {
  background-color: transparent;
  color: #007bff;
  border: 1px solid #007bff;
}

.btn-outline-primary:hover:not(:disabled) {
  background-color: #007bff;
  color: white;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Edit form styles */
.metadata-form {
  max-height: calc(60vh - 2rem);
  overflow-y: auto;
}

.form-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h5 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #495057;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
  font-size: 0.875rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: 0;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-group textarea {
  resize: vertical;
  min-height: 60px;
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
  
  .modal-actions {
    flex-wrap: wrap;
  }
}
</style>
