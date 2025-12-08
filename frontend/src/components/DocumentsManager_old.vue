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
      @documentUpdated="handleDocumentUpdated"
      @documentDeleted="handleDocumentDeleted"
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
            <button @click="exportSelectedMETSXML" class="btn btn-outline">
              <i class="icon-xml"></i> Export METS XML
            </button>
            <button @click="downloadSelectedArchives" class="btn btn-outline">
              <i class="icon-download"></i> Download Archives
            </button>
            <button @click="deleteSelectedDocuments" class="btn btn-outline btn-danger">
              <i class="icon-delete"></i> Delete Selected
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

      <div v-else class="table-wrapper">
        <table class="documents-table">
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
                  <button class="btn btn-sm btn-info dropdown-toggle" @click="toggleDropdown(document.id)" title="Download Options">
                    <i class="icon-download"></i>
                  </button>
                  <div class="dropdown-menu" v-if="openDropdown === document.id" :data-dropdown="document.id">
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
      </div>

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
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
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
      
      // Close dropdown if clicking outside after next tick
      if (openDropdown.value) {
        nextTick(() => {
          // Check if dropdown would go outside viewport and adjust position
          const dropdownElement = document.querySelector(`[data-dropdown="${documentId}"]`)
          if (dropdownElement) {
            const rect = dropdownElement.getBoundingClientRect()
            const viewportWidth = window.innerWidth
            const viewportHeight = window.innerHeight
            
            // Adjust horizontal position if needed
            if (rect.right > viewportWidth - 20) {
              dropdownElement.style.right = '0'
              dropdownElement.style.left = 'auto'
            }
            
            // Adjust vertical position if needed
            if (rect.bottom > viewportHeight - 20) {
              dropdownElement.style.top = 'auto'
              dropdownElement.style.bottom = '100%'
            }
          }
        })
      }
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
      console.log('DocumentsManager: Opening document detail for:', document)
      await loadDocumentDetails(document.id)
    }

    const loadDocumentDetails = async (documentId) => {
      console.log('DocumentsManager: Loading document details for ID:', documentId)
      try {
        loading.value = true
        const url = `${import.meta.env.VITE_API_URL}/api/documents/${documentId}`
        console.log('DocumentsManager: Fetching from URL:', url)
        const response = await axios.get(url, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        console.log('DocumentsManager: Got response:', response.data)
        selectedDocument.value = response.data
        console.log('DocumentsManager: selectedDocument set to:', selectedDocument.value)
      } catch (err) {
        console.error('DocumentsManager: Error loading document details:', err)
        alert('Failed to load document details: ' + (err.response?.data?.detail || err.message))
      } finally {
        loading.value = false
      }
    }

    const handleDocumentUpdated = (updatedDocument) => {
      console.log('Document updated:', updatedDocument)
      
      // Update the document in the list
      const index = documents.value.findIndex(doc => doc.id === updatedDocument.id)
      if (index !== -1) {
        // Update only specific fields that might have changed in the list view
        documents.value[index] = {
          ...documents.value[index],
          logical_id: updatedDocument.logical_id,
          title: updatedDocument.title,
          archive_name: updatedDocument.archive_name,
          document_type: updatedDocument.document_type,
          total_pages: updatedDocument.total_pages,
          updated_at: updatedDocument.updated_at
        }
      }
      
      // Update the selected document if it's the same one
      if (selectedDocument.value && selectedDocument.value.id === updatedDocument.id) {
        selectedDocument.value = updatedDocument
      }
    }

    const handleDocumentDeleted = (documentId) => {
      console.log('Document deleted:', documentId)
      
      // Remove the document from the list
      documents.value = documents.value.filter(doc => doc.id !== documentId)
      
      // Remove from selected documents if it was selected
      selectedDocuments.value = selectedDocuments.value.filter(id => id !== documentId)
      
      // Clear selected document if it was the deleted one
      if (selectedDocument.value && selectedDocument.value.id === documentId) {
        selectedDocument.value = null
      }
      
      // Update pagination if needed
      updatePagination()
    }

    const deleteSelectedDocuments = async () => {
      if (selectedDocuments.value.length === 0) return

      const count = selectedDocuments.value.length
      const documentText = count === 1 ? 'document' : 'documents'
      
      if (!confirm(`Are you sure you want to delete ${count} ${documentText}?\n\nThis will permanently delete:\n- Document metadata\n- All associated files\n- Files from MinIO storage\n\nThis action cannot be undone.`)) {
        return
      }

      const deletingIds = [...selectedDocuments.value]
      let successCount = 0
      let errorCount = 0

      for (const documentId of deletingIds) {
        try {
          const response = await fetch(`${API_URL}/api/documents/${documentId}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'application/json'
            }
          })

          if (response.ok) {
            successCount++
            // Remove from documents list
            documents.value = documents.value.filter(doc => doc.id !== documentId)
            // Remove from selected documents
            selectedDocuments.value = selectedDocuments.value.filter(id => id !== documentId)
          } else {
            errorCount++
            console.error(`Failed to delete document ${documentId}:`, response.statusText)
          }
        } catch (error) {
          errorCount++
          console.error(`Error deleting document ${documentId}:`, error)
        }
      }

      // Show result message
      if (successCount > 0 && errorCount === 0) {
        alert(`Successfully deleted ${successCount} ${successCount === 1 ? 'document' : 'documents'}.`)
      } else if (successCount > 0 && errorCount > 0) {
        alert(`Deleted ${successCount} ${successCount === 1 ? 'document' : 'documents'} successfully.\n${errorCount} ${errorCount === 1 ? 'document' : 'documents'} failed to delete.`)
      } else {
        alert(`Failed to delete ${errorCount} ${errorCount === 1 ? 'document' : 'documents'}.`)
      }

      // Update pagination
      updatePagination()
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
        if (err.response && err.response.status === 404) {
          alert('METS XML not available for this document. The document may not have been processed with METS metadata.')
        } else {
          alert('Error exporting METS XML. Please try again.')
        }
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

    const exportSelectedMETSXML = async () => {
      if (selectedDocuments.value.length === 0) {
        alert('Please select at least one document to export')
        return
      }

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/export/mets`,
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
        link.setAttribute('download', `documents_mets.zip`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Export selected METS XML error:', err)
        if (err.response && err.response.status === 404) {
          alert('No METS XML available for the selected documents')
        } else {
          alert('Error exporting METS XML. Please try again.')
        }
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
      if (!dateString) return '-'
      try {
        const date = new Date(dateString)
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
      } catch {
        return dateString
      }
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
      handleDocumentUpdated,
      handleDocumentDeleted,
      deleteSelectedDocuments,
      exportMetadataCSV,
      exportMETSXML,
      downloadFiles,
      downloadArchive,
      exportSelectedCSV,
      exportSelectedMETSXML,
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
  padding: var(--spacing-xl);
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-primary);
}

.header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-2xl);
  font-weight: 600;
}

.actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
  text-decoration: none;
}

.btn-primary {
  background: var(--primary-color);
  color: var(--text-inverse);
  border-color: var(--primary-color);
}

.btn-primary:hover {
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

.btn-secondary:hover {
  background: var(--bg-tertiary);
  transform: translateY(-1px);
}

.btn-outline {
  background: transparent;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.btn-outline:hover {
  background: var(--primary-color);
  color: var(--text-inverse);
  transform: translateY(-1px);
}

.btn-outline.btn-danger {
  color: var(--accent-danger);
  border-color: var(--accent-danger);
}

.btn-outline.btn-danger:hover {
  background: var(--accent-danger);
  color: var(--text-inverse);
  transform: translateY(-1px);
}

.btn-info {
  background: var(--primary-light);
  color: var(--text-inverse);
  border-color: var(--primary-light);
}

.btn-info:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--text-xs);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(27, 60, 74, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-xl);
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-xl);
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-xl);
  font-weight: 600;
}

.close-btn:hover {
  color: var(--text-primary);
}

.modal-body {
  padding: var(--spacing-xl);
}

/* Table styles */
.table-container {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  /* Remove overflow hidden to allow dropdowns to show */
  overflow: visible;
  box-shadow: var(--shadow-md);
  /* Ensure container has proper stacking context */
  position: relative;
  z-index: 1;
}

.table-wrapper {
  /* Handle horizontal scroll for the table content only */
  overflow-x: auto;
  overflow-y: visible;
}

.table-header {
  padding: var(--spacing-lg) var(--spacing-xl);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
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
  position: relative;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.dropdown {
  position: relative;
}

.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  min-width: 160px;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  /* Ensure dropdown shows above table constraints */
  max-height: none;
  overflow: visible;
  /* Add subtle animation */
  animation: fadeInDropdown 0.2s ease-out;
}

@keyframes fadeInDropdown {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

/* Icons - Modern CSS icons */
.icon-plus::before { content: '+'; }
.icon-eye::before { 
  content: '●';
  font-size: 12px;
}
.icon-download::before { content: '↓'; }
.icon-csv::before { content: '📊'; }
.icon-xml::before { content: '📄'; }
.icon-images::before { content: '🖼'; }
.icon-archive::before { content: '📦'; }
</style>
