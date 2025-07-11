<template>
  <div class="document-upload-form">
    <form @submit.prevent="uploadDocument">
      <div class="form-sections">
        <!-- File Upload Section -->
        <div class="form-section">
          <h4>File Upload</h4>
          <div class="file-upload-area">
            <input 
              ref="fileInput"
              type="file" 
              @change="handleFileSelect"
              accept="image/*"
              required
              class="file-input"
            />
            <div class="file-drop-zone" @click="$refs.fileInput.click()">
              <div v-if="!selectedFile" class="drop-zone-content">
                <div class="upload-icon">📁</div>
                <p>Click to select an image file</p>
                <p class="file-types">Supported: JPG, PNG, TIFF</p>
              </div>
              <div v-else class="selected-file-info">
                <div class="file-icon">📄</div>
                <div class="file-details">
                  <p class="file-name">{{ selectedFile.name }}</p>
                  <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
                </div>
                <button type="button" @click.stop="removeFile" class="remove-file-btn">×</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Basic Metadata Section -->
        <div class="form-section">
          <h4>Basic Information</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="logical_id">Logical ID</label>
              <input 
                type="text" 
                id="logical_id"
                v-model="formData.logical_id"
                placeholder="Auto-compilato dal nome file (opzionale)"
              />
              <small class="field-help">Se lasciato vuoto, verrà utilizzato automaticamente il nome del file caricato</small>
            </div>
            <div class="form-group">
              <label for="title">Title</label>
              <input 
                type="text" 
                id="title"
                v-model="formData.title"
                placeholder="Document title"
              />
            </div>
          </div>
          <div class="form-group">
            <label for="description">Description</label>
            <textarea 
              id="description"
              v-model="formData.description"
              placeholder="Document description"
              rows="3"
            ></textarea>
          </div>
        </div>

        <!-- Archive Information Section -->
        <div class="form-section">
          <h4>Archive Information</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="archive_name">Archive Name</label>
              <input 
                type="text" 
                id="archive_name"
                v-model="formData.archive_name"
                placeholder="e.g., Archivio di stato di Modena"
              />
            </div>
            <div class="form-group">
              <label for="archive_contact">Archive Contact</label>
              <input 
                type="email" 
                id="archive_contact"
                v-model="formData.archive_contact"
                placeholder="e.g., as-mo@cultura.gov.it"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="conservative_id">Conservative ID</label>
              <input 
                type="text" 
                id="conservative_id"
                v-model="formData.conservative_id"
                placeholder="e.g., IT-MO0172"
              />
            </div>
            <div class="form-group">
              <label for="conservative_id_authority">ID Authority</label>
              <input 
                type="text" 
                id="conservative_id_authority"
                v-model="formData.conservative_id_authority"
                placeholder="e.g., ISIL"
              />
            </div>
          </div>
        </div>

        <!-- Technical Information Section -->
        <div class="form-section">
          <h4>Technical Information</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="image_producer">Image Producer</label>
              <input 
                type="text" 
                id="image_producer"
                v-model="formData.image_producer"
                placeholder="e.g., EDS Gamma"
              />
            </div>
            <div class="form-group">
              <label for="scanner_manufacturer">Scanner Manufacturer</label>
              <input 
                type="text" 
                id="scanner_manufacturer"
                v-model="formData.scanner_manufacturer"
                placeholder="e.g., Metis Systems srl"
              />
            </div>
          </div>
          <div class="form-group">
            <label for="scanner_model">Scanner Model</label>
            <input 
              type="text" 
              id="scanner_model"
              v-model="formData.scanner_model"
              placeholder="e.g., METIS EDS Gamma integrated with a : Nikon D850 DigitalCamera"
            />
          </div>
        </div>

        <!-- Document Structure Section -->
        <div class="form-section">
          <h4>Document Structure</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="document_type">Document Type</label>
              <select id="document_type" v-model="formData.document_type">
                <option value="">Select type</option>
                <option value="book">Book</option>
                <option value="manuscript">Manuscript</option>
                <option value="document">Document</option>
                <option value="map">Map</option>
                <option value="photograph">Photograph</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div class="form-group">
              <label for="total_pages">Total Pages</label>
              <input 
                type="number" 
                id="total_pages"
                v-model.number="formData.total_pages"
                min="1"
                placeholder="Number of pages"
              />
            </div>
          </div>
        </div>

        <!-- File Metadata Section -->
        <div class="form-section">
          <h4>File Metadata</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="file_use">File Use</label>
              <select id="file_use" v-model="formData.file_use">
                <option value="">Select use</option>
                <option value="ARCHIVE">Archive</option>
                <option value="HIGH">High Resolution</option>
                <option value="MEDIUM">Medium Resolution</option>
                <option value="THUMBNAIL">Thumbnail</option>
              </select>
            </div>
            <div class="form-group">
              <label for="file_label">File Label</label>
              <input 
                type="text" 
                id="file_label"
                v-model="formData.file_label"
                placeholder="e.g., Dorso, Piatto anteriore"
              />
            </div>
          </div>
          <div class="form-group">
            <label for="sequence_number">Sequence Number</label>
            <input 
              type="number" 
              id="sequence_number"
              v-model.number="formData.sequence_number"
              min="0"
              placeholder="Order in sequence"
            />
          </div>
        </div>

        <!-- Rights Information Section -->
        <div class="form-section">
          <h4>Rights Information</h4>
          <div class="form-group">
            <label for="license_url">License URL</label>
            <input 
              type="url" 
              id="license_url"
              v-model="formData.license_url"
              placeholder="e.g., https://w3id.org/italia/controlled-vocabulary/licences/BC_Standard_1.0"
            />
          </div>
          <div class="form-group">
            <label for="rights_statement">Rights Statement</label>
            <input 
              type="url" 
              id="rights_statement"
              v-model="formData.rights_statement"
              placeholder="e.g., http://rightsstatements.org/vocab/NoC-OKLR/1.0/"
            />
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" @click="$emit('cancel')" class="btn btn-outline">
          Cancel
        </button>
        <button type="submit" :disabled="uploading" class="btn btn-primary">
          {{ uploading ? 'Uploading...' : 'Upload Document' }}
        </button>
      </div>
    </form>

    <!-- Upload Progress -->
    <div v-if="uploading" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <p class="progress-text">{{ uploadStatus }}</p>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

export default {
  name: 'DocumentUploadForm',
  emits: ['upload-complete', 'cancel'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    const selectedFile = ref(null)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const error = ref('')
    const logicalIdAutoFilled = ref(false) // Track if logical_id was auto-filled

    const formData = reactive({
      logical_id: '',
      title: '',
      description: '',
      archive_name: '',
      archive_contact: '',
      conservative_id: '',
      conservative_id_authority: '',
      image_producer: '',
      scanner_manufacturer: '',
      scanner_model: '',
      document_type: '',
      total_pages: null,
      file_use: '',
      file_label: '',
      sequence_number: null,
      license_url: '',
      rights_statement: ''
    })

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
        error.value = ''
        
        // Auto-populate logical_id if it's empty
        if (!formData.logical_id) {
          // Remove file extension from the filename
          const fileNameWithoutExtension = file.name.replace(/\.[^/.]+$/, "")
          formData.logical_id = fileNameWithoutExtension
          logicalIdAutoFilled.value = true
        }
      }
    }

    const removeFile = () => {
      selectedFile.value = null
      const fileInput = document.querySelector('.file-input')
      if (fileInput) fileInput.value = ''
      
      // Clear logical_id if it was auto-filled
      if (logicalIdAutoFilled.value) {
        formData.logical_id = ''
        logicalIdAutoFilled.value = false
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const uploadDocument = async () => {
      if (!selectedFile.value) {
        error.value = 'Please select a file'
        return
      }

      uploading.value = true
      uploadProgress.value = 0
      uploadStatus.value = 'Preparing upload...'
      error.value = ''

      try {
        const formDataToSend = new FormData()
        formDataToSend.append('file', selectedFile.value)
        
        // Add all form fields
        for (const [key, value] of Object.entries(formData)) {
          if (value !== null && value !== '') {
            formDataToSend.append(key, value)
          }
        }

        uploadStatus.value = 'Uploading document...'
        
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/upload`,
          formDataToSend,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              uploadProgress.value = progress
              uploadStatus.value = `Uploading... ${progress}%`
            }
          }
        )

        uploadStatus.value = 'Upload complete!'
        uploadProgress.value = 100
        
        setTimeout(() => {
          emit('upload-complete', response.data)
        }, 1000)

      } catch (err) {
        error.value = err.response?.data?.detail || err.message
        uploadStatus.value = 'Upload failed'
      } finally {
        uploading.value = false
      }
    }

    // Watch for manual changes to logical_id
    watch(() => formData.logical_id, (newValue, oldValue) => {
      // If user manually modifies the field, mark it as not auto-filled
      if (logicalIdAutoFilled.value && oldValue && newValue !== oldValue) {
        logicalIdAutoFilled.value = false
      }
    })

    return {
      selectedFile,
      formData,
      uploading,
      uploadProgress,
      uploadStatus,
      error,
      handleFileSelect,
      removeFile,
      formatFileSize,
      uploadDocument
    }
  }
}
</script>

<style scoped>
.document-upload-form {
  max-width: 900px;
  margin: 0 auto;
}

.form-sections {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.form-section {
  background: var(--bg-secondary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-sm);
}

.form-section h4 {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--text-primary);
  font-size: var(--text-lg);
  font-weight: 600;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.field-help {
  margin-top: var(--spacing-xs);
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-style: italic;
}

.form-group input,
.form-group select,
.form-group textarea {
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
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(50, 169, 195, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-group select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right var(--spacing-sm) center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

.file-upload-area {
  margin-bottom: var(--spacing-xl);
}

.file-input {
  display: none;
}

.file-drop-zone {
  border: 2px dashed var(--primary-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-2xl);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-normal);
  background: var(--bg-primary);
  box-shadow: var(--shadow-sm);
}

.file-drop-zone:hover {
  border-color: var(--primary-dark);
  background: var(--primary-lighter);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
}

.upload-icon {
  font-size: 3rem;
  color: var(--primary-color);
}

.drop-zone-content p {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-base);
  font-weight: 500;
}

.file-types {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.selected-file-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  background: var(--bg-primary);
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-sm);
}

.file-icon {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.file-details {
  flex: 1;
}

.file-name {
  margin: 0;
  font-weight: 500;
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.file-size {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.remove-file-btn {
  background: var(--accent-danger);
  color: var(--text-inverse);
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  cursor: pointer;
  font-size: var(--text-sm);
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.remove-file-btn:hover {
  background: var(--accent-danger-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-2xl);
  padding-top: var(--spacing-xl);
  border-top: 1px solid var(--border-primary);
}

.btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.btn-primary {
  background: var(--primary-color);
  color: var(--text-inverse);
  border-color: var(--primary-color);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: var(--bg-primary);
  color: var(--text-primary);
  border-color: var(--border-secondary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-tertiary);
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.upload-progress {
  margin-top: var(--spacing-xl);
  padding: var(--spacing-lg);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-sm);
}

.progress-bar {
  background: var(--bg-muted);
  border-radius: var(--radius-sm);
  height: 10px;
  overflow: hidden;
  margin-bottom: var(--spacing-sm);
}

.progress-fill {
  background: var(--primary-color);
  height: 100%;
  transition: width var(--transition-normal);
}

.progress-text {
  margin: 0;
  text-align: center;
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 500;
}

.error-message {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background: #FEE2E2;
  color: #991B1B;
  border: 1px solid #FECACA;
  border-radius: var(--radius-md);
}

.error-message p {
  margin: 0;
  font-size: var(--text-sm);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>

