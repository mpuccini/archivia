<template>
  <div class="excel-batch-import">
    <!-- Intestazione -->
    <div class="form-header">
      <file-excel-outlined :style="{ fontSize: '32px', color: '#52c41a', marginBottom: '16px' }" />
      <h1>Importazione Batch da Excel</h1>
      <p>Carica un file Excel (.xlsx) con i metadati dei documenti per creare più documenti contemporaneamente</p>
    </div>

    <!-- Loading Overlay -->
    <a-spin :spinning="isProcessing || isCreating" :tip="isProcessing ? 'Elaborazione file Excel...' : 'Creazione documenti...'">
      <!-- Step 1: File Upload -->
      <a-card v-if="currentStep === 1" :bordered="false" class="upload-card">
        <!-- Istruzioni -->
        <a-alert
          message="Formato del file Excel"
          type="info"
          show-icon
          style="margin-bottom: 24px"
        >
          <template #icon>
            <inbox-outlined />
          </template>
          <template #description>
            <div>
              <p>Il file Excel deve contenere una riga di intestazione con i nomi dei campi.</p>
              <p style="margin-top: 8px;">I campi supportati includono: <strong>logical_id</strong> (obbligatorio), title, archive_name, document_type, creator, subject, description, publisher, date_created, language, format, identifier, rights, coverage, total_pages, notes.</p>
              <a-button
                type="link"
                size="small"
                @click="downloadTemplate"
                style="padding-left: 0; margin-top: 8px;"
              >
                <template #icon>
                  <download-outlined />
                </template>
                Scarica template di esempio
              </a-button>
            </div>
          </template>
        </a-alert>

        <!-- File Upload Area -->
        <a-upload-dragger
          v-model:file-list="fileList"
          name="excel_file"
          accept=".xlsx,.xls"
          :multiple="false"
          :before-upload="beforeUpload"
          :show-upload-list="false"
          @change="handleFileChange"
          @drop="handleDrop"
        >
          <p class="ant-upload-drag-icon">
            <file-excel-outlined :style="{ fontSize: '48px', color: '#52c41a' }" />
          </p>
          <p class="ant-upload-text" style="font-size: 16px; font-weight: 500;">
            Trascina il file Excel qui o clicca per sfogliare
          </p>
          <p class="ant-upload-hint" style="color: #8c8c8c;">
            Supporta file Excel (.xlsx, .xls) fino a 10MB
          </p>
        </a-upload-dragger>

        <!-- Selected File -->
        <div v-if="selectedFile" style="margin-top: 24px;">
          <a-alert
            type="success"
            show-icon
          >
            <template #icon>
              <check-circle-outlined />
            </template>
            <template #message>
              <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-weight: 600;">File Excel Selezionato</span>
                <a @click="removeFile" style="color: #ff4d4f; font-weight: 500;">
                  Rimuovi
                </a>
              </div>
            </template>
            <template #description>
              <div style="margin-top: 8px;">
                <p style="font-weight: 500; margin: 0;">{{ selectedFile.name }}</p>
                <p style="font-size: 12px; color: #8c8c8c; margin: 4px 0 0 0;">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
            </template>
          </a-alert>
        </div>

        <!-- Actions -->
        <div style="display: flex; justify-content: space-between; margin-top: 24px;">
          <a-button size="large" @click="$emit('cancel')">
            <template #icon>
              <close-outlined />
            </template>
            Annulla
          </a-button>
          <a-button
            type="primary"
            size="large"
            @click="parseExcelFile"
            :disabled="!selectedFile"
            :loading="isProcessing"
          >
            <template #icon>
              <upload-outlined />
            </template>
            {{ isProcessing ? 'Elaborazione...' : 'Analizza File' }}
          </a-button>
        </div>
      </a-card>

      <!-- Step 2: Preview and Confirm -->
      <a-card v-if="currentStep === 2" :bordered="false" class="preview-card">
        <div class="step-header">
          <h3>Anteprima Documenti</h3>
          <p>Rivedi i {{ parsedDocuments.length }} documenti che verranno creati. Puoi modificare i singoli campi se necessario.</p>
        </div>

        <!-- Error Messages -->
        <a-alert
          v-if="parseErrors.length > 0"
          message="Problemi di Elaborazione"
          type="warning"
          show-icon
          style="margin-bottom: 24px"
        >
          <template #description>
            <ul style="margin: 0; padding-left: 20px;">
              <li v-for="error in parseErrors" :key="error">{{ error }}</li>
            </ul>
          </template>
        </a-alert>

        <!-- Documents Preview Table -->
        <a-table
          :columns="tableColumns"
          :data-source="parsedDocuments"
          :pagination="{ pageSize: 10 }"
          :scroll="{ x: 1200 }"
          :row-class-name="(record) => record.hasErrors ? 'error-row' : ''"
          style="margin-bottom: 24px"
        >
          <template #bodyCell="{ column, record, index }">
            <template v-if="column.key === 'row'">
              {{ index + 2 }}
            </template>
            <template v-else-if="column.key === 'logical_id'">
              <a-input
                v-model:value="record.logical_id"
                :status="!record.logical_id ? 'error' : ''"
                size="small"
              />
            </template>
            <template v-else-if="column.key === 'title'">
              <a-input v-model:value="record.title" size="small" />
            </template>
            <template v-else-if="column.key === 'archive_name'">
              <a-input v-model:value="record.archive_name" size="small" />
            </template>
            <template v-else-if="column.key === 'document_type'">
              <a-input v-model:value="record.document_type" size="small" />
            </template>
            <template v-else-if="column.key === 'creator'">
              <a-input v-model:value="record.creator" size="small" />
            </template>
            <template v-else-if="column.key === 'status'">
              <a-tag v-if="!record.logical_id" color="error">
                <template #icon>
                  <close-circle-outlined />
                </template>
                ID Mancante
              </a-tag>
              <a-tag v-else color="success">
                <template #icon>
                  <check-circle-outlined />
                </template>
                Pronto
              </a-tag>
            </template>
          </template>
        </a-table>

        <!-- Actions -->
        <div style="display: flex; justify-content: space-between; margin-top: 24px;">
          <a-button size="large" @click="currentStep = 1">
            <template #icon>
              <arrow-left-outlined />
            </template>
            Indietro
          </a-button>
          <a-button
            type="primary"
            size="large"
            @click="createDocuments"
            :disabled="!canCreateDocuments"
            :loading="isCreating"
          >
            <template #icon>
              <check-circle-outlined />
            </template>
            {{ isCreating ? 'Creazione in corso...' : `Crea ${validDocuments.length} Documenti` }}
          </a-button>
        </div>
      </a-card>

      <!-- Step 3: Results -->
      <a-card v-if="currentStep === 3" :bordered="false" class="results-card">
        <!-- Success Result -->
        <a-result
          v-if="importResults.errors.length === 0"
          status="success"
          title="Importazione Completata con Successo!"
          :sub-title="`${importResults.success.length} documenti sono stati creati correttamente.`"
        >
          <template #icon>
            <check-circle-outlined />
          </template>
          <template #extra>
            <a-button type="primary" size="large" @click="$emit('import-complete')">
              Chiudi
            </a-button>
          </template>
        </a-result>

        <!-- Partial Success Result -->
        <a-result
          v-else-if="importResults.success.length > 0"
          status="warning"
          title="Importazione Completata Parzialmente"
          :sub-title="`${importResults.success.length} documenti creati con successo, ${importResults.errors.length} errori.`"
        >
          <template #icon>
            <exclamation-circle-outlined />
          </template>
        </a-result>

        <!-- Error Result -->
        <a-result
          v-else
          status="error"
          title="Importazione Fallita"
          :sub-title="`Nessun documento è stato creato. ${importResults.errors.length} errori riscontrati.`"
        >
          <template #icon>
            <close-circle-outlined />
          </template>
        </a-result>

        <!-- Statistics Row -->
        <a-row :gutter="16" style="margin: 32px 0;" v-if="importResults.success.length > 0 || importResults.errors.length > 0">
          <a-col :span="12">
            <a-card>
              <a-statistic
                title="Documenti Creati"
                :value="importResults.success.length"
                :value-style="{ color: '#52c41a' }"
              >
                <template #prefix>
                  <check-circle-outlined />
                </template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card>
              <a-statistic
                title="Errori"
                :value="importResults.errors.length"
                :value-style="{ color: '#ff4d4f' }"
              >
                <template #prefix>
                  <close-circle-outlined />
                </template>
              </a-statistic>
            </a-card>
          </a-col>
        </a-row>

        <!-- Success List -->
        <a-alert
          v-if="importResults.success.length > 0"
          message="Documenti Creati con Successo"
          type="success"
          show-icon
          style="margin-bottom: 16px"
        >
          <template #description>
            <div style="max-height: 200px; overflow-y: auto;">
              <ul style="margin: 0; padding-left: 20px;">
                <li v-for="result in importResults.success" :key="result.logical_id">
                  <strong>{{ result.logical_id }}</strong> - {{ result.title || 'Senza titolo' }}
                </li>
              </ul>
            </div>
          </template>
        </a-alert>

        <!-- Error List -->
        <a-alert
          v-if="importResults.errors.length > 0"
          message="Errori di Creazione"
          type="error"
          show-icon
          style="margin-bottom: 24px"
        >
          <template #description>
            <div style="max-height: 200px; overflow-y: auto;">
              <ul style="margin: 0; padding-left: 20px;">
                <li v-for="error in importResults.errors" :key="error.logical_id">
                  <strong>{{ error.logical_id }}</strong>: {{ error.error }}
                </li>
              </ul>
            </div>
          </template>
        </a-alert>

        <!-- Actions -->
        <div style="display: flex; justify-content: flex-end; margin-top: 24px;">
          <a-button type="primary" size="large" @click="$emit('import-complete')">
            Chiudi
          </a-button>
        </div>
      </a-card>
    </a-spin>
  </div>
</template>

<script>
import { ref, computed, h } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { message } from 'ant-design-vue'
import {
  FileExcelOutlined,
  UploadOutlined,
  InboxOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CloseOutlined,
  DownloadOutlined,
  ArrowLeftOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'ExcelBatchImport',
  components: {
    FileExcelOutlined,
    UploadOutlined,
    InboxOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    CloseOutlined,
    DownloadOutlined,
    ArrowLeftOutlined,
    ExclamationCircleOutlined
  },
  emits: ['import-complete', 'cancel'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    const currentStep = ref(1)
    const selectedFile = ref(null)
    const fileList = ref([])
    const isProcessing = ref(false)
    const isCreating = ref(false)
    const parsedDocuments = ref([])
    const parseErrors = ref([])
    const importResults = ref({ success: [], errors: [] })

    // Table columns for preview
    const tableColumns = [
      {
        title: 'Riga',
        key: 'row',
        width: 80,
        fixed: 'left'
      },
      {
        title: 'ID Logico',
        key: 'logical_id',
        width: 150,
        fixed: 'left'
      },
      {
        title: 'Titolo',
        key: 'title',
        width: 200
      },
      {
        title: 'Archivio',
        key: 'archive_name',
        width: 150
      },
      {
        title: 'Tipo',
        key: 'document_type',
        width: 150
      },
      {
        title: 'Creatore',
        key: 'creator',
        width: 150
      },
      {
        title: 'Stato',
        key: 'status',
        width: 120,
        fixed: 'right'
      }
    ]

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

    const beforeUpload = (file) => {
      if (!file.name.match(/\.(xlsx|xls)$/i)) {
        message.error('Seleziona un file Excel (.xlsx o .xls)')
        return false
      }

      if (file.size > 10 * 1024 * 1024) {
        message.error('Il file deve essere inferiore a 10MB')
        return false
      }

      selectedFile.value = file
      return false // Prevent auto upload
    }

    const handleFileChange = (info) => {
      // File is handled in beforeUpload
    }

    const handleDrop = (e) => {
      // Handled by a-upload-dragger
    }

    const removeFile = () => {
      selectedFile.value = null
      fileList.value = []
    }

    const downloadTemplate = () => {
      // Create template Excel file
      const templateData = [
        ['logical_id', 'title', 'archive_name', 'document_type', 'creator', 'subject', 'description', 'publisher', 'date_created', 'language', 'format', 'identifier', 'rights', 'coverage', 'total_pages', 'notes'],
        ['DOC001', 'Esempio Documento 1', 'Archivio Storico', 'Manoscritto', 'Mario Rossi', 'Storia', 'Descrizione del documento', 'Editore Esempio', '2024-01-15', 'ita', 'Cartaceo', 'ID-001', 'Pubblico dominio', 'Italia', '10', 'Note varie']
      ]

      const ws = XLSX.utils.aoa_to_sheet(templateData)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, 'Documenti')
      XLSX.writeFile(wb, 'template_importazione_documenti.xlsx')
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
          throw new Error('Il file Excel deve contenere almeno una riga di intestazione e una riga di dati')
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
              parseErrors.value.push(`Riga ${rowIndex + 2}: ID logico mancante`)
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
          throw new Error('Nessun dato documento valido trovato nel file Excel')
        }

        parsedDocuments.value = documents
        currentStep.value = 2
        message.success(`${documents.length} documenti analizzati con successo`)

      } catch (error) {
        console.error('Error parsing Excel file:', error)
        message.error('Errore durante l\'elaborazione del file Excel: ' + error.message)
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

        // Show success message
        if (response.data.errors.length === 0) {
          message.success(`Tutti i ${response.data.success.length} documenti sono stati creati con successo!`)
        } else if (response.data.success.length > 0) {
          message.warning(`${response.data.success.length} documenti creati, ${response.data.errors.length} errori`)
        } else {
          message.error('Nessun documento è stato creato a causa di errori')
        }

      } catch (error) {
        console.error('Error creating documents:', error)
        message.error('Errore durante la creazione dei documenti: ' + (error.response?.data?.detail || error.message))
      } finally {
        isCreating.value = false
      }
    }

    return {
      h,
      currentStep,
      selectedFile,
      fileList,
      isProcessing,
      isCreating,
      parsedDocuments,
      parseErrors,
      importResults,
      validDocuments,
      canCreateDocuments,
      tableColumns,
      formatFileSize,
      beforeUpload,
      handleFileChange,
      handleDrop,
      removeFile,
      downloadTemplate,
      parseExcelFile,
      createDocuments
    }
  }
}
</script>

<style scoped>
.excel-batch-import {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
  margin: 16px 0 8px 0;
}

.form-header p {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

.upload-card,
.preview-card,
.results-card {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02);
}

.step-header {
  margin-bottom: 24px;
}

.step-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.step-header p {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

:deep(.error-row) {
  background-color: #fff2f0;
}

:deep(.error-row:hover > td) {
  background-color: #ffebe8 !important;
}
</style>
