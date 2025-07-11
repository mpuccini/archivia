<template>
  <div class="documents-manager">
    <div class="header">
      <h2>Document Management</h2>
      <div class="actions">
        <button @click="showUploadForm = true" class="btn btn-primary">
          <i class="icon-plus"></i> New Document
        </button>
      </div>
    </div>

    <!-- Upload Form Modal -->
    <div v-if="showUploadForm" class="modal-overlay" @click="closeUploadForm">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Upload New Document</h3>
          <button @click="closeUploadForm" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <DocumentUploadForm @upload-complete="handleUploadComplete" @cancel="closeUploadForm" />
        </div>
      </div>
    </div>

    <!-- Document Detail Modal -->
    <DocumentDetailModal 
      v-if="selectedDocument" 
      :document="selectedDocument" 
      @close="selectedDocument = null" 
    />

    <!-- Documents Table -->
    <div class="table-container">
      <div class="table-header">
        <div class="table-controls">
          <div class="selection-info" v-if="selectedDocuments.length > 0">
            {{ selectedDocuments.length }} document(s) selected
          </div>
          <div class="batch-actions" v-if="selectedDocuments.length > 0">
            <button @click="exportSelectedCSV" class="btn btn-outline">
              <i class="icon-csv"></i> Export CSV
            </button>
            <button @click="downloadSelectedArchives" class="btn btn-outline">
              <i class="icon-download"></i> Download Archives
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <p>Loading documents...</p>
      </div>

      <div v-else-if="error" class="error">
        <p>Error loading documents: {{ error }}</p>
        <button @click="loadDocuments" class="btn btn-primary">Retry</button>
      </div>

      <table v-else class="documents-table">
        <thead>
          <tr>
            <th class="checkbox-column">
              <input 
                type="checkbox" 
                :checked="allSelected"
                @change="toggleAllSelection"
              >
            </th>
            <th>Logical ID</th>
            <th>Title</th>
            <th>Archive</th>
            <th>Type</th>
            <th>Pages</th>
            <th>Files</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="document in documents" :key="document.id" class="document-row" @click="openDocumentDetail(document)">
            <td class="checkbox-column" @click.stop>
              <input 
                type="checkbox" 
                :value="document.id"
                v-model="selectedDocuments"
              >
            </td>
            <td class="logical-id">{{ document.logical_id }}</td>
            <td class="title">{{ document.title || '-' }}</td>
            <td class="archive">{{ document.archive_name || '-' }}</td>
            <td class="type">{{ document.document_type || '-' }}</td>
            <td class="pages">{{ document.total_pages || '-' }}</td>
            <td class="files">{{ document.file_count }}</td>
            <td class="created">{{ formatDate(document.created_at) }}</td>
            <td class="actions" @click.stop>
              <div class="action-buttons">
                <button @click="viewDocument(document)" class="btn btn-sm btn-info" title="View Details">
                  <i class="icon-eye"></i>
                </button>
                <div class="dropdown">
                  <button class="btn btn-sm btn-secondary dropdown-toggle" @click="toggleDropdown(document.id)">
                    <i class="icon-download"></i>
                  </button>
                  <div class="dropdown-menu" v-if="openDropdown === document.id">
                    <a href="#" @click.prevent="exportMetadataCSV(document.id)" class="dropdown-item">
                      <i class="icon-csv"></i> Export CSV
                    </a>
                    <a href="#" @click.prevent="exportMETSXML(document.id)" class="dropdown-item">
                      <i class="icon-xml"></i> Export METS XML
                    </a>
                    <a href="#" @click.prevent="downloadFiles(document.id)" class="dropdown-item">
                      <i class="icon-images"></i> Download Files
                    </a>
                    <a href="#" @click.prevent="downloadArchive(document.id)" class="dropdown-item">
                      <i class="icon-archive"></i> Download Archive
                    </a>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!loading && documents.length === 0" class="empty-state">
        <p>No documents found.</p>
        <button @click="showUploadForm = true" class="btn btn-primary">
          Upload your first document
        </button>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn btn-outline"
      >
        Previous
      </button>
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button 
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="btn btn-outline"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import DocumentUploadForm from './DocumentUploadForm.vue'
import DocumentDetailModal from './DocumentDetailModal.vue'
import axios from 'axios'

export default {
  name: 'DocumentsManager',
  components: {
    DocumentUploadForm,
    DocumentDetailModal
  },
  setup() {
    const authStore = useAuthStore()
    const documents = ref([])
    const selectedDocuments = ref([])
    const selectedDocument = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const showUploadForm = ref(false)
    const openDropdown = ref(null)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const pageSize = 20

    const allSelected = computed(() => {
      return documents.value.length > 0 && selectedDocuments.value.length === documents.value.length
    })

    const loadDocuments = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents/`, {
          params: {
            skip: (currentPage.value - 1) * pageSize,
            limit: pageSize
          },
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        documents.value = response.data
        // Calculate total pages (this would need to be returned from the API)
        totalPages.value = Math.ceil(documents.value.length / pageSize)
      } catch (err) {
        error.value = err.response?.data?.detail || err.message
      } finally {
        loading.value = false
      }
    }

    const toggleAllSelection = () => {
      if (allSelected.value) {
        selectedDocuments.value = []
      } else {
        selectedDocuments.value = documents.value.map(doc => doc.id)
      }
    }

    const toggleDropdown = (documentId) => {
      openDropdown.value = openDropdown.value === documentId ? null : documentId
    }

    const closeUploadForm = () => {
      showUploadForm.value = false
    }

    const handleUploadComplete = () => {
      closeUploadForm()
      loadDocuments()
    }

    const viewDocument = async (document) => {
      await loadDocumentDetails(document.id)
    }

    const openDocumentDetail = async (document) => {
      await loadDocumentDetails(document.id)
    }

    const loadDocumentDetails = async (documentId) => {
      try {
        loading.value = true
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/documents/${documentId}`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          }
        )
        selectedDocument.value = response.data
      } catch (err) {
        console.error('Error loading document details:', err)
      } finally {
        loading.value = false
      }
    }

    const exportMetadataCSV = async (documentId) => {
      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/export/csv`,
          [documentId],
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `document_${documentId}_metadata.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Export CSV error:', err)
      }
      openDropdown.value = null
    }

    const exportMETSXML = async (documentId) => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/documents/${documentId}/export/mets`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `document_${documentId}_mets.xml`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Export METS XML error:', err)
      }
      openDropdown.value = null
    }

    const downloadFiles = async (documentId) => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/documents/${documentId}/download/files`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `document_${documentId}_files.zip`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Download files error:', err)
      }
      openDropdown.value = null
    }

    const downloadArchive = async (documentId) => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/documents/${documentId}/download/archive`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `document_${documentId}_archive.zip`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Download archive error:', err)
      }
      openDropdown.value = null
    }

    const exportSelectedCSV = async () => {
      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/export/csv`,
          selectedDocuments.value,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `documents_metadata.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Export selected CSV error:', err)
      }
    }

    const downloadSelectedArchives = async () => {
      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/download/batch`,
          selectedDocuments.value,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `documents_batch.zip`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Download selected archives error:', err)
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadDocuments()
      }
    }

    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (!event.target.closest('.dropdown')) {
        openDropdown.value = null
      }
    }

    onMounted(() => {
      loadDocuments()
      document.addEventListener('click', handleClickOutside)
    })

    return {
      documents,
      selectedDocuments,
      selectedDocument,
      loading,
      error,
      showUploadForm,
      openDropdown,
      currentPage,
      totalPages,
      allSelected,
      loadDocuments,
      toggleAllSelection,
      toggleDropdown,
      closeUploadForm,
      handleUploadComplete,
      viewDocument,
      openDocumentDetail,
      loadDocumentDetails,
      exportMetadataCSV,
      exportMETSXML,
      downloadFiles,
      downloadArchive,
      exportSelectedCSV,
      downloadSelectedArchives,
      formatDate,
      goToPage
    }
  }
}
</script>

<style scoped>
.documents-manager {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
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

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-info:hover {
  background: #138496;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

/* Table styles */
.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table-header {
  padding: 15px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selection-info {
  font-weight: 500;
  color: #495057;
}

.batch-actions {
  display: flex;
  gap: 10px;
}

.documents-table {
  width: 100%;
  border-collapse: collapse;
}

.documents-table th,
.documents-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.documents-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.checkbox-column {
  width: 40px;
  text-align: center;
}

.logical-id {
  font-family: monospace;
  font-size: 13px;
  color: #495057;
}

.document-row:hover {
  background: #f8f9fa;
}

.actions {
  width: 120px;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.dropdown {
  position: relative;
}

.dropdown-toggle {
  border: none;
  background: #6c757d;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  min-width: 160px;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dropdown-item {
  display: block;
  padding: 8px 12px;
  color: #495057;
  text-decoration: none;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.page-info {
  font-size: 14px;
  color: #6c757d;
}

/* Icons (placeholder - you would use a real icon library) */
.icon-plus::before { content: '+'; }
.icon-eye::before { content: '👁'; }
.icon-download::before { content: '↓'; }
.icon-csv::before { content: '📊'; }
.icon-xml::before { content: '📄'; }
.icon-images::before { content: '🖼'; }
.icon-archive::before { content: '📦'; }
</style>
