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
              <label for="logical_id">Logical ID *</label>
              <input 
                type="text" 
                id="logical_id"
                v-model="formData.logical_id"
                required
                placeholder="e.g., ASMO_T-CONCORDI-POSS-281822"
              />
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
import { ref, reactive } from 'vue'
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
      }
    }

    const removeFile = () => {
      selectedFile.value = null
      const fileInput = document.querySelector('.file-input')
      if (fileInput) fileInput.value = ''
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
  max-width: 800px;
  margin: 0 auto;
}

.form-sections {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.form-section h4 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 16px;
  font-weight: 600;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: 500;
  color: #495057;
  font-size: 14px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

/* File upload styles */
.file-upload-area {
  margin-bottom: 20px;
}

.file-input {
  display: none;
}

.file-drop-zone {
  border: 2px dashed #007bff;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.file-drop-zone:hover {
  border-color: #0056b3;
  background: #f8f9ff;
}

.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.upload-icon {
  font-size: 48px;
  color: #007bff;
}

.drop-zone-content p {
  margin: 0;
  color: #495057;
}

.file-types {
  font-size: 12px;
  color: #6c757d;
}

.selected-file-info {
  display: flex;
  align-items: center;
  gap: 15px;
  background: white;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.file-icon {
  font-size: 24px;
  color: #007bff;
}

.file-details {
  flex: 1;
}

.file-name {
  margin: 0;
  font-weight: 500;
  color: #495057;
}

.file-size {
  margin: 0;
  font-size: 12px;
  color: #6c757d;
}

.remove-file-btn {
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

.remove-file-btn:hover {
  background: #c82333;
}

/* Form actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.btn-outline {
  background: white;
  color: #007bff;
  border: 1px solid #007bff;
}

.btn-outline:hover {
  background: #007bff;
  color: white;
}

/* Upload progress */
.upload-progress {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.progress-bar {
  background: #e9ecef;
  border-radius: 4px;
  height: 8px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  background: #007bff;
  height: 100%;
  transition: width 0.3s;
}

.progress-text {
  margin: 0;
  text-align: center;
  color: #495057;
  font-size: 14px;
}

/* Error message */
.error-message {
  margin-top: 15px;
  padding: 12px;
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.error-message p {
  margin: 0;
}

/* Responsive design */
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
