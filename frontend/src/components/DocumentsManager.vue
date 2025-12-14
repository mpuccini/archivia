<template>
  <div class="space-y-6">
    <!-- Header with actions -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Gestione Documenti</h2>
        <p class="mt-1 text-sm text-gray-600">Gestisci e organizza i tuoi archivi digitali</p>
      </div>
      <div class="mt-4 sm:mt-0">
        <a-space :size="12">
          <a-button
            type="primary"
            @click="showUploadForm = true"
            size="large"
          >
            <template #icon>
              <PlusOutlined />
            </template>
            Nuovo Documento
          </a-button>

          <a-dropdown>
            <template #overlay>
              <a-menu>
                <a-menu-item key="excel" @click="showExcelBatchImport = true">
                  <FileExcelOutlined style="color: #52c41a;" />
                  <span class="ml-2">Importa da Excel</span>
                </a-menu-item>
                <a-menu-item key="images" @click="showBatchImageUpload = true">
                  <PictureOutlined style="color: #722ed1;" />
                  <span class="ml-2">Carica Immagini in Batch</span>
                </a-menu-item>
                <a-menu-item key="folder" @click="showFolderUpload = true">
                  <FolderOutlined style="color: #1890ff;" />
                  <span class="ml-2">Carica Cartella ECO-MiC</span>
                </a-menu-item>
              </a-menu>
            </template>
            <a-button size="large" style="background: #52c41a; border-color: #52c41a; color: white;">
              <InboxOutlined />
              Operazioni in Batch
              <DownOutlined />
            </a-button>
          </a-dropdown>
        </a-space>
      </div>
    </div>

    <!-- Selection Actions Bar -->
    <div v-if="selectedDocuments.length > 0" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-blue-900">
          {{ selectedDocuments.length }} {{ selectedDocuments.length === 1 ? 'documento selezionato' : 'documenti selezionati' }}
        </span>
        <a-space>
          <a-button @click="exportSelectedCSV" size="small" :loading="exporting">
            <template #icon>
              <ExportOutlined />
            </template>
            Esporta CSV
          </a-button>
          <a-button @click="exportSelectedMETSXML" type="primary" size="small" :loading="exportingMets">
            <template #icon>
              <FileTextOutlined />
            </template>
            Esporta METS XML
          </a-button>
          <a-button @click="downloadSelectedArchives" type="primary" size="small" :loading="downloadingArchives">
            <template #icon>
              <DownloadOutlined />
            </template>
            Scarica Archivi
          </a-button>
          <a-button @click="showDeleteConfirm = true" danger size="small" :loading="deleting">
            <template #icon>
              <DeleteOutlined />
            </template>
            Elimina Selezionati
          </a-button>
        </a-space>
      </div>
    </div>

    <!-- Loading State -->
    <a-spin v-if="loading" size="large" :spinning="loading">
      <div class="text-center py-12">
        <p class="text-gray-600">Caricamento documenti...</p>
      </div>
    </a-spin>

    <!-- Error State -->
    <a-alert
      v-else-if="error"
      type="error"
      :message="'Errore nel caricamento dei documenti'"
      :description="error"
      show-icon
      closable
    >
      <template #action>
        <a-button size="small" danger @click="loadDocuments">
          Riprova
        </a-button>
      </template>
    </a-alert>

    <!-- Empty State -->
    <a-empty v-else-if="documents.length === 0" description="Nessun documento">
      <template #image>
        <FileTextOutlined style="font-size: 48px; color: #d9d9d9;" />
      </template>
      <p class="mt-1 text-sm text-gray-500">Inizia caricando il tuo primo documento.</p>
      <a-button type="primary" @click="showUploadForm = true" class="mt-4">
        <template #icon>
          <UploadOutlined />
        </template>
        Carica Documento
      </a-button>
    </a-empty>

    <!-- Documents Table -->
    <a-table
      v-else
      :columns="columns"
      :data-source="documents"
      :row-key="record => record.id"
      :pagination="pagination"
      :row-selection="rowSelection"
      @change="handleTableChange"
      :loading="loading"
      :scroll="{ x: 1200 }"
      :custom-row="(record) => ({
        onClick: () => openDocumentDetail(record)
      })"
    >
      <!-- Logical ID Column -->
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'logical_id'">
          <a-typography-text strong @click="openDocumentDetail(record)" style="cursor: pointer; color: #1890ff;">
            {{ record.logical_id }}
          </a-typography-text>
        </template>

        <!-- Title Column -->
        <template v-else-if="column.key === 'title'">
          {{ record.title || '-' }}
        </template>

        <!-- Archive Column -->
        <template v-else-if="column.key === 'archive_name'">
          {{ record.archive_name || '-' }}
        </template>

        <!-- Type Column -->
        <template v-else-if="column.key === 'document_type'">
          <a-tag v-if="record.document_type" color="default">
            {{ record.document_type }}
          </a-tag>
          <span v-else>-</span>
        </template>

        <!-- Pages Column -->
        <template v-else-if="column.key === 'total_pages'">
          {{ record.total_pages || '-' }}
        </template>

        <!-- Files Column -->
        <template v-else-if="column.key === 'file_count'">
          <a-tag color="blue">{{ record.file_count }}</a-tag>
        </template>

        <!-- Created Column -->
        <template v-else-if="column.key === 'created_at'">
          {{ formatDate(record.created_at) }}
        </template>

        <!-- Actions Column -->
        <template v-else-if="column.key === 'actions'">
          <a-space :size="8">
            <a-tooltip title="Visualizza Dettagli">
              <a-button
                type="link"
                size="small"
                @click.stop="viewDocument(record)"
              >
                <template #icon>
                  <EyeOutlined />
                </template>
              </a-button>
            </a-tooltip>

            <a-dropdown>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="download" @click="downloadDocumentFiles(record)">
                    <DownloadOutlined />
                    <span class="ml-2">Scarica File</span>
                  </a-menu-item>
                  <a-menu-item key="archive" @click="downloadDocumentArchive(record)">
                    <FileZipOutlined />
                    <span class="ml-2">Scarica Archivio</span>
                  </a-menu-item>
                  <a-menu-item key="mets" @click="exportMETSXML(record.id)">
                    <FileTextOutlined />
                    <span class="ml-2">Esporta METS XML</span>
                  </a-menu-item>
                </a-menu>
              </template>
              <a-button type="link" size="small" @click.stop>
                <template #icon>
                  <DownOutlined />
                </template>
              </a-button>
            </a-dropdown>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- Upload Form Modal -->
    <a-modal
      v-model:open="showUploadForm"
      title="Carica Nuovo Documento"
      :footer="null"
      :width="1200"
      :mask-style="modalMaskStyle"
      wrapClassName="blur-modal"
      @cancel="closeUploadForm"
    >
      <DocumentUploadForm @upload-complete="handleUploadComplete" @cancel="closeUploadForm" />
    </a-modal>

    <!-- Excel Batch Import Modal -->
    <a-modal
      v-model:open="showExcelBatchImport"
      title="Importazione Batch da Excel"
      :footer="null"
      :width="1400"
      :mask-style="modalMaskStyle"
      wrapClassName="blur-modal"
      @cancel="closeExcelBatchImport"
    >
      <ExcelBatchImport @import-complete="handleExcelImportComplete" @cancel="closeExcelBatchImport" />
    </a-modal>

    <!-- Batch Image Upload Modal -->
    <a-modal
      v-model:open="showBatchImageUpload"
      title="Caricamento Batch Immagini"
      :footer="null"
      :width="1200"
      :mask-style="modalMaskStyle"
      wrapClassName="blur-modal"
      @cancel="closeBatchImageUpload"
    >
      <BatchImageUpload @upload-complete="handleBatchImageUploadComplete" @cancel="closeBatchImageUpload" />
    </a-modal>

    <!-- Folder Upload Modal -->
    <a-modal
      v-model:open="showFolderUpload"
      title="Carica Cartella ECO-MiC"
      :footer="null"
      :width="1000"
      :mask-style="modalMaskStyle"
      wrapClassName="blur-modal"
      @cancel="closeFolderUpload"
    >
      <FolderUpload @success="handleFolderUploadComplete" @cancel="closeFolderUpload" />
    </a-modal>

    <!-- Delete Confirmation Modal -->
    <a-modal
      v-model:open="showDeleteConfirm"
      title="Conferma Eliminazione"
      :confirm-loading="isDeleting"
      :mask-style="modalMaskStyle"
      wrapClassName="blur-modal"
      @ok="confirmDelete"
      @cancel="showDeleteConfirm = false"
    >
      <a-alert
        type="warning"
        :message="`Sei sicuro di voler eliminare ${selectedDocuments.length} ${selectedDocuments.length === 1 ? 'documento' : 'documenti'}?`"
        description="Questa azione non può essere annullata."
        show-icon
      />
    </a-modal>

    <!-- Document Detail Modal -->
    <a-modal
      v-model:open="showDocumentDetail"
      title="Dettagli Documento"
      :footer="null"
      :width="1200"
      :mask-style="modalMaskStyle"
      wrapClassName="blur-modal"
      @cancel="closeDocumentDetail"
    >
      <DocumentDetailModal
        v-if="selectedDocument"
        :document="selectedDocument"
        @close="closeDocumentDetail"
        @updated="handleDocumentUpdated"
        @deleted="handleDocumentDeleted"
      />
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, h } from 'vue'
import { useAuthStore } from '../stores/auth'
import {
  PlusOutlined,
  InboxOutlined,
  DownOutlined,
  FileExcelOutlined,
  PictureOutlined,
  FolderOutlined,
  DownloadOutlined,
  FileTextOutlined,
  DeleteOutlined,
  UploadOutlined,
  EyeOutlined,
  FileZipOutlined,
  ExportOutlined
} from '@ant-design/icons-vue'
import DocumentUploadForm from './DocumentUploadForm.vue'
import DocumentDetailModal from './DocumentDetailModal.vue'
import ExcelBatchImport from './ExcelBatchImport.vue'
import BatchImageUpload from './BatchImageUpload.vue'
import FolderUpload from './FolderUpload.vue'
import axios from 'axios'
import { message } from 'ant-design-vue'

export default {
  name: 'DocumentsManager',
  components: {
    DocumentUploadForm,
    DocumentDetailModal,
    ExcelBatchImport,
    BatchImageUpload,
    FolderUpload,
    PlusOutlined,
    InboxOutlined,
    DownOutlined,
    FileExcelOutlined,
    PictureOutlined,
    FolderOutlined,
    DownloadOutlined,
    FileTextOutlined,
    DeleteOutlined,
    UploadOutlined,
    EyeOutlined,
    FileZipOutlined,
    ExportOutlined
  },
  setup() {
    const authStore = useAuthStore()
    const documents = ref([])
    const selectedDocuments = ref([])
    const selectedDocument = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const showUploadForm = ref(false)
    const showExcelBatchImport = ref(false)
    const showBatchImageUpload = ref(false)
    const showFolderUpload = ref(false)
    const showDeleteConfirm = ref(false)
    const showDocumentDetail = ref(false)
    const isDeleting = ref(false)
    const exporting = ref(false)
    const exportingMets = ref(false)
    const downloadingArchives = ref(false)
    const deleting = ref(false)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const totalDocuments = ref(0)
    const pageSize = 20

    // Stile per sfondo sfocato delle modali
    const modalMaskStyle = {
      backdropFilter: 'blur(8px)',
      WebkitBackdropFilter: 'blur(8px)',
      backgroundColor: 'rgba(0, 0, 0, 0.60)'
    }

    // Table columns configuration
    const columns = [
      {
        title: 'ID Logico',
        dataIndex: 'logical_id',
        key: 'logical_id',
        width: 150,
        fixed: 'left'
      },
      {
        title: 'Titolo',
        dataIndex: 'title',
        key: 'title',
        width: 250,
        ellipsis: true
      },
      {
        title: 'Archivio',
        dataIndex: 'archive_name',
        key: 'archive_name',
        width: 200,
        ellipsis: true
      },
      {
        title: 'Tipo',
        dataIndex: 'document_type',
        key: 'document_type',
        width: 150
      },
      {
        title: 'Pagine',
        dataIndex: 'total_pages',
        key: 'total_pages',
        width: 100,
        align: 'center'
      },
      {
        title: 'File',
        dataIndex: 'file_count',
        key: 'file_count',
        width: 100,
        align: 'center'
      },
      {
        title: 'Creato',
        dataIndex: 'created_at',
        key: 'created_at',
        width: 120
      },
      {
        title: 'Azioni',
        key: 'actions',
        width: 120,
        fixed: 'right',
        align: 'center'
      }
    ]

    // Row selection configuration
    const rowSelection = {
      selectedRowKeys: selectedDocuments,
      onChange: (selectedRowKeys) => {
        selectedDocuments.value = selectedRowKeys
      },
      getCheckboxProps: (record) => ({
        name: record.logical_id
      })
    }

    // Pagination configuration
    const pagination = computed(() => ({
      current: currentPage.value,
      pageSize: pageSize,
      total: totalDocuments.value,
      showSizeChanger: false,
      showTotal: (total, range) => `Mostrando ${range[0]}-${range[1]} di ${total} documenti`
    }))

    const loadDocuments = async () => {
      console.log('[DocumentsManager] loadDocuments called, currentPage:', currentPage.value)
      loading.value = true
      error.value = null

      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents`, {
          params: {
            page: currentPage.value,
            size: pageSize
          },
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })

        console.log('[DocumentsManager] loadDocuments response:', response.data)
        documents.value = response.data.documents || response.data.items || response.data

        if (response.data.total_pages) {
          totalPages.value = response.data.total_pages
        } else if (response.data.pages) {
          totalPages.value = response.data.pages
        }

        if (response.data.total) {
          totalDocuments.value = response.data.total
        } else if (response.data.total_count) {
          totalDocuments.value = response.data.total_count
        }

      } catch (err) {
        console.error('Error loading documents:', err)
        error.value = err.response?.data?.detail || err.message || 'Impossibile caricare i documenti'
      } finally {
        loading.value = false
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

    const handleTableChange = (pag) => {
      currentPage.value = pag.current
      loadDocuments()
    }

    const closeUploadForm = () => {
      showUploadForm.value = false
    }

    const closeExcelBatchImport = () => {
      showExcelBatchImport.value = false
    }

    const closeBatchImageUpload = () => {
      showBatchImageUpload.value = false
    }

    const closeFolderUpload = () => {
      showFolderUpload.value = false
    }

    const closeDocumentDetail = () => {
      showDocumentDetail.value = false
      selectedDocument.value = null
    }

    const handleUploadComplete = () => {
      closeUploadForm()
      loadDocuments()
      message.success('Documento caricato con successo')
    }

    const handleExcelImportComplete = () => {
      closeExcelBatchImport()
      loadDocuments()
      message.success('Importazione Excel completata')
    }

    const handleBatchImageUploadComplete = () => {
      closeBatchImageUpload()
      loadDocuments()
      message.success('Caricamento immagini completato')
    }

    const handleFolderUploadComplete = (data) => {
      console.log('[DocumentsManager] handleFolderUploadComplete called with:', data)
      closeFolderUpload()
      console.log('[DocumentsManager] Calling loadDocuments...')
      loadDocuments()
      message.success('Caricamento cartella completato')
    }

    const handleDocumentUpdated = () => {
      closeDocumentDetail()
      loadDocuments()
      message.success('Documento aggiornato con successo')
    }

    const handleDocumentDeleted = () => {
      closeDocumentDetail()
      loadDocuments()
      message.success('Documento eliminato con successo')
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
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents/${documentId}`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        selectedDocument.value = response.data
        showDocumentDetail.value = true
      } catch (err) {
        console.error('Error loading document details:', err)
        message.error('Impossibile caricare i dettagli del documento: ' + (err.response?.data?.detail || err.message))
      } finally {
        loading.value = false
      }
    }

    const exportSelectedCSV = async () => {
      if (selectedDocuments.value.length === 0) {
        message.warning('Seleziona almeno un documento')
        return
      }

      exporting.value = true

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/export/csv`,
          { document_ids: selectedDocuments.value },
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )

        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `documenti_export_${Date.now()}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        message.success(`Esportazione CSV completata: ${selectedDocuments.value.length} ${selectedDocuments.value.length === 1 ? 'documento' : 'documenti'}`)
      } catch (err) {
        console.error('Error exporting CSV:', err)
        message.error('Errore durante l\'esportazione CSV')
      } finally {
        exporting.value = false
      }
    }

    const exportSelectedMETSXML = async () => {
      if (selectedDocuments.value.length === 0) {
        message.warning('Seleziona almeno un documento')
        return
      }

      if (selectedDocuments.value.length > 1) {
        message.info('L\'esportazione METS è supportata solo per un documento alla volta. Verrà esportato il primo documento selezionato.')
      }

      exportingMets.value = true
      try {
        await exportMETSXML(selectedDocuments.value[0])
      } finally {
        exportingMets.value = false
      }
    }

    const exportMETSXML = async (documentId) => {
      try {
        message.loading({ content: 'Generazione e validazione METS XML in corso...', key: 'mets', duration: 0 })

        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/documents/${documentId}/export/mets`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )

        const blob = new Blob([response.data], { type: 'application/xml' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url

        const doc = documents.value.find(d => d.id === documentId)
        const filename = doc?.logical_id || documentId
        link.setAttribute('download', `${filename}_mets.xml`)

        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        message.success({
          content: '✅ METS XML validato ed esportato con successo secondo lo standard ECO-MiC 1.1',
          key: 'mets',
          duration: 4
        })
      } catch (err) {
        console.error('Error exporting METS XML:', err)

        // Handle validation errors (HTTP 422)
        if (err.response?.status === 422) {
          let errorMessage = 'Errore di validazione METS'

          // Parse error from blob response
          if (err.response?.data instanceof Blob) {
            try {
              const text = await err.response.data.text()
              const errorData = JSON.parse(text)
              errorMessage = errorData.detail || errorMessage
            } catch (parseErr) {
              console.error('Failed to parse error response:', parseErr)
            }
          } else if (err.response?.data?.detail) {
            errorMessage = err.response.data.detail
          } else if (typeof err.response?.data === 'string') {
            errorMessage = err.response.data
          }

          // Display detailed validation error with multiline support
          message.error({
            content: h('div', { style: 'white-space: pre-line; max-width: 600px;' }, [
              h('strong', '❌ Validazione METS fallita'),
              h('br'),
              h('br'),
              errorMessage
            ]),
            key: 'mets',
            duration: 15  // Longer duration for error messages so user can read them
          })

          // Also log to console for debugging
          console.error('METS validation failed:', errorMessage)
        }
        // Handle service unavailable (HTTP 503)
        else if (err.response?.status === 503) {
          let errorDetail = 'Servizio di validazione non disponibile'

          // Parse error from blob response
          if (err.response?.data instanceof Blob) {
            try {
              const text = await err.response.data.text()
              const errorData = JSON.parse(text)
              errorDetail = errorData.detail || errorDetail
            } catch (parseErr) {
              console.error('Failed to parse error response:', parseErr)
            }
          } else if (err.response?.data?.detail) {
            errorDetail = err.response.data.detail
          }

          message.error({
            content: h('div', { style: 'white-space: pre-line;' }, `⚠️ ${errorDetail}`),
            key: 'mets',
            duration: 10
          })
        }
        // Handle other errors
        else {
          message.error({
            content: 'Errore durante l\'esportazione METS XML. Riprova più tardi.',
            key: 'mets',
            duration: 5
          })
        }
      }
    }

    const downloadSelectedArchives = async () => {
      if (selectedDocuments.value.length === 0) {
        message.warning('Seleziona almeno un documento')
        return
      }

      downloadingArchives.value = true

      try {
        message.loading({ content: 'Preparazione archivi in corso...', key: 'archive', duration: 0 })

        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/download/archives`,
          { document_ids: selectedDocuments.value },
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )

        const blob = new Blob([response.data], { type: 'application/zip' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `archivi_${Date.now()}.zip`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        message.success({ content: `Archivi scaricati con successo: ${selectedDocuments.value.length} ${selectedDocuments.value.length === 1 ? 'documento' : 'documenti'}`, key: 'archive', duration: 2 })
      } catch (err) {
        console.error('Error downloading archives:', err)
        message.error({ content: 'Errore durante lo scaricamento degli archivi', key: 'archive', duration: 3 })
      } finally {
        downloadingArchives.value = false
      }
    }

    const downloadDocumentFiles = async (document) => {
      message.info('Download file documento: ' + document.logical_id)
    }

    const downloadDocumentArchive = async (document) => {
      try {
        message.loading({ content: 'Preparazione archivio in corso...', key: 'doc-archive', duration: 0 })

        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/documents/${document.id}/download`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )

        const blob = new Blob([response.data], { type: 'application/zip' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${document.logical_id}_archive.zip`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        message.success({ content: 'Archivio scaricato con successo', key: 'doc-archive', duration: 2 })
      } catch (err) {
        console.error('Error downloading document archive:', err)
        message.error({ content: 'Errore durante lo scaricamento dell\'archivio', key: 'doc-archive', duration: 3 })
      }
    }

    const confirmDelete = async () => {
      if (selectedDocuments.value.length === 0) {
        return
      }

      isDeleting.value = true
      deleting.value = true

      try {
        const count = selectedDocuments.value.length

        await axios.delete(
          `${import.meta.env.VITE_API_URL}/api/documents/batch`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            data: { document_ids: selectedDocuments.value }
          }
        )

        message.success(`${count} ${count === 1 ? 'documento eliminato' : 'documenti eliminati'} con successo`)
        selectedDocuments.value = []
        showDeleteConfirm.value = false
        await loadDocuments()
      } catch (err) {
        console.error('Error deleting documents:', err)
        message.error('Errore durante l\'eliminazione: ' + (err.response?.data?.detail || err.message))
      } finally {
        isDeleting.value = false
        deleting.value = false
      }
    }

    onMounted(() => {
      loadDocuments()
    })

    return {
      documents,
      selectedDocuments,
      selectedDocument,
      loading,
      error,
      modalMaskStyle,
      showUploadForm,
      showExcelBatchImport,
      showBatchImageUpload,
      showFolderUpload,
      showDeleteConfirm,
      showDocumentDetail,
      isDeleting,
      exporting,
      exportingMets,
      downloadingArchives,
      deleting,
      currentPage,
      totalPages,
      columns,
      rowSelection,
      pagination,
      loadDocuments,
      formatDate,
      handleTableChange,
      closeUploadForm,
      closeExcelBatchImport,
      closeBatchImageUpload,
      closeFolderUpload,
      closeDocumentDetail,
      handleUploadComplete,
      handleExcelImportComplete,
      handleBatchImageUploadComplete,
      handleFolderUploadComplete,
      handleDocumentUpdated,
      handleDocumentDeleted,
      viewDocument,
      openDocumentDetail,
      exportSelectedCSV,
      exportSelectedMETSXML,
      exportMETSXML,
      downloadSelectedArchives,
      downloadDocumentFiles,
      downloadDocumentArchive,
      confirmDelete
    }
  }
}
</script>

<style scoped>
/* Custom styles for table interactions */
:deep(.ant-table-row) {
  cursor: pointer;
}

:deep(.ant-table-row:hover) {
  background-color: #f5f5f5;
}
</style>
