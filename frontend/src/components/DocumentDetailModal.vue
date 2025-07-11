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
            style="display: block !important; visibility: visible !important;"
          >
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
          <button 
            v-if="isEditing" 
            @click="deleteDocument" 
            class="btn btn-sm btn-danger delete-btn"
            :disabled="deleting"
            style="display: block !important; visibility: visible !important; background-color: #dc3545 !important; color: white !important;"
          >
            {{ deleting ? 'Deleting...' : 'Delete Document' }}
          </button>
          <button 
            v-if="isEditing" 
            @click="cancelEdit" 
            class="btn btn-sm btn-secondary cancel-btn"
            :disabled="saving || deleting"
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
                  <div class="file-actions">
                    <button 
                      @click.stop="downloadFile(file)" 
                      class="btn btn-sm btn-outline-primary download-btn"
                      title="Download file"
                    >
                      ⬇
                    </button>
                    <button 
                      v-if="isEditing"
                      @click.stop="deleteFile(file)" 
                      class="btn btn-sm btn-outline-danger delete-file-btn"
                      title="Delete file"
                      :disabled="deletingFileId === file.file_id"
                      style="display: inline-block !important; visibility: visible !important; background-color: transparent !important; color: #dc3545 !important; border: 1px solid #dc3545 !important;"
                    >
                      {{ deletingFileId === file.file_id ? '...' : '🗑' }}
                    </button>
                  </div>
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
                    @click="openImageViewer"
                    class="preview-image clickable"
                    title="Click to view full size"
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
    
    <!-- Image Viewer -->
    <ImageViewer
      v-if="selectedFile && isImageFile(selectedFile)"
      :visible="showImageViewer"
      :imageUrl="imageDataUrl"
      :filename="selectedFile.filename"
      :imageWidth="selectedFile.image_width"
      :imageHeight="selectedFile.image_height"
      :fileSize="selectedFile.file_size"
      @close="closeImageViewer"
    />
  </div>
</template>

<script>
import { ref, reactive, watch, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import ImageViewer from './ImageViewer.vue'

export default {
  name: 'DocumentDetailModal',
  components: {
    ImageViewer
  },
  props: {
    document: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'documentUpdated', 'documentDeleted'],
  setup(props, { emit }) {
    console.log('DocumentDetailModal: Component setup called with document:', props.document)
    console.log('DocumentDetailModal: Document files:', props.document?.document_files)
    const authStore = useAuthStore()
    const selectedFile = ref(null)
    const imageLoaded = ref(false)
    const imageError = ref(false)
    const imageDataUrl = ref('')
    
    // Image viewer state
    const showImageViewer = ref(false)
    
    // Edit state
    const isEditing = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const deletingFileId = ref(null)
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

    const isImageFile = (file) => {
      if (!file.content_type) return false
      return file.content_type.startsWith('image/')
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

    const openImageViewer = () => {
      if (selectedFile.value && isImageFile(selectedFile.value) && imageLoaded.value) {
        showImageViewer.value = true
      }
    }

    const closeImageViewer = () => {
      showImageViewer.value = false
    }

    // Edit functions
    const startEdit = () => {
      console.log('startEdit called, setting isEditing to true')
      isEditing.value = true
      console.log('isEditing is now:', isEditing.value)
      // Initialize form with current document data
      Object.keys(editForm).forEach(key => {
        editForm[key] = props.document[key] || (key === 'total_pages' ? null : '')
      })
    }

    const cancelEdit = () => {
      isEditing.value = false
      saving.value = false
      deleting.value = false
      deletingFileId.value = null
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

    // Delete functions
    const deleteFile = async (file) => {
      if (!confirm(`Are you sure you want to delete the file "${file.filename}"?\n\nThis action cannot be undone.`)) {
        return
      }

      deletingFileId.value = file.file_id
      try {
        const token = authStore.token
        const response = await axios.delete(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/files/${file.file_id}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        )

        if (response.status === 200) {
          // Remove the file from the document's file list
          const fileIndex = props.document.document_files.findIndex(f => f.file_id === file.file_id)
          if (fileIndex > -1) {
            props.document.document_files.splice(fileIndex, 1)
          }
          
          // Clear selected file if it was the deleted one
          if (selectedFile.value && selectedFile.value.file_id === file.file_id) {
            selectedFile.value = null
            imageDataUrl.value = ''
          }

          console.log('File deleted successfully')
          emit('documentUpdated', props.document)
        }
      } catch (error) {
        console.error('Error deleting file:', error)
        const errorMessage = error.response?.data?.detail || 'Failed to delete file'
        alert(`Error: ${errorMessage}`)
      } finally {
        deletingFileId.value = null
      }
    }

    const deleteDocument = async () => {
      if (!confirm(`Are you sure you want to delete the document "${props.document.title || props.document.logical_id}"?\n\nThis will permanently delete:\n- Document metadata\n- All associated files\n- Files from MinIO storage\n\nThis action cannot be undone.`)) {
        return
      }

      deleting.value = true
      try {
        const token = authStore.token
        const response = await axios.delete(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${props.document.id}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        )

        if (response.status === 200) {
          console.log('Document deleted successfully')
          emit('documentDeleted', props.document.id)
          emit('close')
        }
      } catch (error) {
        console.error('Error deleting document:', error)
        const errorMessage = error.response?.data?.detail || 'Failed to delete document'
        alert(`Error: ${errorMessage}`)
      } finally {
        deleting.value = false
      }
    }

    return {
      selectedFile,
      imageLoaded,
      imageError,
      imageDataUrl,
      showImageViewer,
      isEditing,
      saving,
      deleting,
      deletingFileId,
      editForm,
      selectFile,
      loadImageData,
      formatDate,
      formatFileSize,
      isImageFile,
      downloadFile,
      downloadArchive,
      openImageViewer,
      closeImageViewer,
      startEdit,
      cancelEdit,
      saveChanges,
      deleteFile,
      deleteDocument
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
  background-color: rgba(27, 60, 74, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-primary);
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
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-secondary);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: var(--leading-tight);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
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
  padding: var(--spacing-lg);
  overflow-y: auto;
}

.metadata-panel {
  border-right: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.files-panel {
  background: var(--bg-primary);
}

.metadata-panel h4, .files-panel h4 {
  margin: 0 0 var(--spacing-lg) 0;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.metadata-display .metadata-item {
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-primary);
}

.metadata-item label {
  font-weight: 600;
  color: var(--text-secondary);
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--text-sm);
}

.metadata-item span, .metadata-item a {
  color: var(--text-primary);
  word-break: break-word;
  font-size: var(--text-sm);
}

.metadata-item a {
  color: var(--primary-color);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.metadata-item a:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.file-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: var(--spacing-lg);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.file-item:last-child {
  border-bottom: none;
}

.file-item:hover {
  background-color: var(--bg-secondary);
}

.file-item.selected {
  background-color: var(--primary-lighter);
  border-left: 3px solid var(--primary-color);
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
  font-size: var(--text-sm);
}

.file-meta {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.file-meta span {
  margin-right: var(--spacing-md);
}

.file-actions {
  display: flex;
  gap: var(--spacing-xs);
  align-items: center;
}

.download-btn, .delete-file-btn {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--text-xs);
}

.file-preview {
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--bg-primary);
}

.file-preview h5 {
  margin: 0;
  padding: var(--spacing-md);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
}

.preview-content {
  padding: var(--spacing-lg);
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}

.preview-image.clickable {
  cursor: pointer;
  transition: all var(--transition-normal);
}

.preview-image.clickable:hover {
  transform: scale(1.02);
  box-shadow: var(--shadow-lg);
}

.loading-preview, .error-preview {
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
  font-style: italic;
  font-size: var(--text-sm);
}

.file-info-preview {
  text-align: left;
}

.file-icon {
  font-size: var(--text-3xl);
  text-align: center;
  margin-bottom: var(--spacing-lg);
  opacity: 0.6;
}

.file-details p {
  margin: var(--spacing-sm) 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.file-details strong {
  color: var(--text-primary);
}

.no-files, .no-preview {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-muted);
}

.no-preview-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.no-preview-icon {
  font-size: var(--text-3xl);
  margin-bottom: var(--spacing-lg);
  opacity: 0.4;
}

.modal-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-secondary);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
}

.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}

.btn-primary {
  background-color: var(--primary-color);
  color: var(--text-inverse);
  border-color: var(--primary-color);
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-dark);
  border-color: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border-color: var(--border-secondary);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--bg-tertiary);
  transform: translateY(-1px);
}

.btn-outline-primary {
  background-color: transparent;
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.btn-outline-primary:hover:not(:disabled) {
  background-color: var(--primary-color);
  color: var(--text-inverse);
  transform: translateY(-1px);
}

.btn-outline-danger {
  background-color: transparent;
  color: var(--accent-danger);
  border-color: var(--accent-danger);
}

.btn-outline-danger:hover:not(:disabled) {
  background-color: var(--accent-danger);
  color: var(--text-inverse);
  transform: translateY(-1px);
}

.btn-danger {
  background-color: var(--accent-danger);
  color: var(--text-inverse);
  border-color: var(--accent-danger);
}

.btn-danger:hover:not(:disabled) {
  background-color: #DC2626;
  border-color: #DC2626;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--text-xs);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

/* Edit form styles */
.metadata-form {
  max-height: calc(60vh - 2rem);
  overflow-y: auto;
}

.form-section {
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-primary);
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h5 {
  margin: 0 0 var(--spacing-lg) 0;
  font-size: var(--text-base);
  color: var(--text-primary);
  font-weight: 600;
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  font-family: var(--font-sans);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(50, 169, 195, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-group select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right var(--spacing-sm) center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
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
  
  .modal-header {
    padding: var(--spacing-md);
  }
  
  .modal-header h3 {
    font-size: var(--text-lg);
  }
  
  .metadata-panel, .files-panel {
    padding: var(--spacing-md);
  }
}
</style>
