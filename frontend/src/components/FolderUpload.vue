<template>
  <div class="folder-upload-container">
    <!-- Intestazione -->
    <div class="form-header">
      <folder-outlined :style="{ fontSize: '32px', color: '#1890ff', marginBottom: '16px' }" />
      <h1>Carica Struttura Cartella ECO-MiC</h1>
      <p>Carica una struttura completa di documenti con categorizzazione automatica dei file</p>
    </div>

    <a-card :bordered="false" class="upload-card">
      <!-- Istruzioni di Caricamento -->
      <a-alert
        message="Carica Archivio ZIP"
        description="Comprimi la tua struttura di cartelle ECO-MiC in un archivio ZIP. La cartella deve contenere le directory standard ECO-MiC (TIF.Master, JPG300, JPG150, Metadata, ICC, Logs, ecc.)."
        type="info"
        show-icon
        :icon="h(InboxOutlined)"
        style="margin-bottom: 24px"
      />

      <!-- Area di Upload Drag & Drop -->
      <a-upload-dragger
        v-model:file-list="fileList"
        name="zip_file"
        accept=".zip"
        :multiple="false"
        :before-upload="beforeUpload"
        :show-upload-list="false"
        @change="handleFileChange"
        @drop="handleDrop"
      >
        <p class="ant-upload-drag-icon">
          <file-zip-outlined :style="{ fontSize: '48px', color: '#1890ff' }" />
        </p>
        <p class="ant-upload-text" style="font-size: 16px; font-weight: 500;">
          Trascina il file ZIP qui o clicca per sfogliare
        </p>
        <p class="ant-upload-hint" style="color: #8c8c8c;">
          Supporta archivi .zip fino a 5GB
        </p>
      </a-upload-dragger>

      <!-- File Selezionato -->
      <div v-if="selectedFile" style="margin-top: 24px;">
        <a-alert
          type="success"
          :message="h('div', { style: 'display: flex; align-items: center; justify-content: space-between;' }, [
            h('div', { style: 'display: flex; align-items: center;' }, [
              h(CheckCircleOutlined, { style: 'margin-right: 8px; color: #52c41a' }),
              h('span', { style: 'font-weight: 600;' }, 'Archivio ZIP Selezionato')
            ]),
            h('a', {
              onClick: clearFiles,
              style: 'color: #ff4d4f; font-weight: 500; cursor: pointer;'
            }, 'Cancella')
          ])"
          show-icon
        >
          <template #description>
            <div style="margin-top: 8px;">
              <p style="font-weight: 500; margin: 0;">{{ selectedFile.name }}</p>
              <p style="font-size: 12px; color: #8c8c8c; margin: 4px 0 0 0;">{{ formatFileSize(selectedFile.size) }}</p>
            </div>
          </template>
        </a-alert>
      </div>

      <!-- Form Metadati Documento -->
      <div v-if="selectedFile" style="margin-top: 32px;">
        <a-divider orientation="left">
          <file-text-outlined /> Informazioni Documento
        </a-divider>

        <a-form
          :model="formData"
          layout="vertical"
          :label-col="{ span: 24 }"
          :wrapper-col="{ span: 24 }"
        >
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item
                label="ID Logico"
                name="logical_id"
                :rules="[{ required: true, message: 'L\'ID logico è obbligatorio' }]"
              >
                <a-input
                  v-model:value="formData.logical_id"
                  placeholder="es. DOC_2025_001"
                  size="large"
                >
                  <template #prefix>
                    <file-outlined style="color: rgba(0, 0, 0, 0.25)" />
                  </template>
                </a-input>
              </a-form-item>
            </a-col>

            <a-col :span="12">
              <a-form-item
                label="ID Conservativo"
                name="conservative_id"
              >
                <a-input
                  v-model:value="formData.conservative_id"
                  placeholder="es. IT-MO0172"
                  size="large"
                >
                  <template #prefix>
                    <folder-outlined style="color: rgba(0, 0, 0, 0.25)" />
                  </template>
                </a-input>
              </a-form-item>
            </a-col>
          </a-row>

          <a-form-item
            label="Titolo"
            name="title"
            :rules="[{ required: true, message: 'Il titolo è obbligatorio' }]"
          >
            <a-input
              v-model:value="formData.title"
              placeholder="Titolo del documento"
              size="large"
            />
          </a-form-item>

          <a-form-item
            label="Descrizione"
            name="description"
          >
            <a-textarea
              v-model:value="formData.description"
              placeholder="Descrizione del documento"
              :rows="3"
              size="large"
            />
          </a-form-item>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item
                label="Nome Archivio"
                name="archive_name"
              >
                <a-input
                  v-model:value="formData.archive_name"
                  placeholder="Nome dell'istituzione archivistica"
                  size="large"
                />
              </a-form-item>
            </a-col>

            <a-col :span="12">
              <a-form-item
                label="Contatto Archivio"
                name="archive_contact"
              >
                <a-input
                  v-model:value="formData.archive_contact"
                  placeholder="Informazioni di contatto"
                  size="large"
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item
                label="Tipo di Documento"
                name="document_type"
              >
                <a-select
                  v-model:value="formData.document_type"
                  placeholder="Seleziona tipo..."
                  size="large"
                >
                  <a-select-option value="">Seleziona tipo...</a-select-option>
                  <a-select-option value="risorsa manoscritta">Risorsa manoscritta</a-select-option>
                  <a-select-option value="documento testuale">Documento testuale</a-select-option>
                  <a-select-option value="risorsa a stampa">Risorsa a stampa</a-select-option>
                  <a-select-option value="risorsa cartografica">Risorsa cartografica</a-select-option>
                  <a-select-option value="risorsa grafica">Risorsa grafica</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>

            <a-col :span="12">
              <a-form-item
                label="Autorità ID Conservativo"
                name="conservative_id_authority"
              >
                <a-input
                  v-model:value="formData.conservative_id_authority"
                  placeholder="es. ISIL"
                  size="large"
                />
              </a-form-item>
            </a-col>
          </a-row>
        </a-form>
      </div>

      <!-- Progresso Caricamento -->
      <div v-if="isUploading" style="margin-top: 24px;">
        <a-card :bordered="false" style="background-color: #e6f7ff; border: 1px solid #91d5ff;">
          <a-spin :indicator="h(LoadingOutlined, { style: 'fontSize: 24px' })" :spinning="true">
            <div style="padding: 24px 0;">
              <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-weight: 500; color: #0050b3;">Caricamento in corso...</span>
                <span style="font-weight: 600; color: #0050b3;">{{ uploadProgress }}%</span>
              </div>
              <a-progress
                :percent="uploadProgress"
                status="active"
                :show-info="false"
              />
              <p style="font-size: 12px; color: #0050b3; margin-top: 8px; margin-bottom: 0;">
                {{ uploadStatus }}
              </p>
            </div>
          </a-spin>
        </a-card>
      </div>

      <!-- Risultato Caricamento -->
      <div v-if="uploadResult" style="margin-top: 24px;">
        <!-- Successo -->
        <a-result
          v-if="uploadResult.success"
          status="success"
          :title="uploadResult.message"
          sub-title="Il documento è stato caricato e i file sono stati categorizzati correttamente"
        >
          <template #icon>
            <check-circle-outlined style="color: #52c41a" />
          </template>
          <template #extra>
            <!-- File Categorizzati -->
            <div v-if="uploadResult.categorized_files" style="margin-top: 16px; text-align: left;">
              <a-descriptions
                :title="`File categorizzati (${uploadResult.total_files} totali):`"
                bordered
                size="small"
                :column="2"
              >
                <a-descriptions-item
                  v-for="(files, category) in uploadResult.categorized_files"
                  :key="category"
                  :label="formatCategory(category)"
                  :span="1"
                >
                  <div>
                    <div style="font-weight: 600; color: #52c41a;">{{ files.length }} file</div>
                    <div style="font-size: 12px; color: #8c8c8c; margin-top: 4px;">
                      {{ files[0]?.file_use || '' }}
                    </div>
                  </div>
                </a-descriptions-item>
              </a-descriptions>
            </div>
          </template>
        </a-result>

        <!-- Errore -->
        <a-result
          v-else
          status="error"
          title="Caricamento Fallito"
          :sub-title="uploadResult.message"
        >
          <template #icon>
            <close-circle-outlined style="color: #ff4d4f" />
          </template>
          <template #extra>
            <a-alert
              v-if="uploadResult.error"
              :message="uploadResult.error"
              type="error"
              show-icon
            />
          </template>
        </a-result>
      </div>

      <!-- Pulsanti Azione -->
      <div style="margin-top: 32px; display: flex; justify-content: flex-end; gap: 12px;">
        <a-button
          v-if="!uploadResult"
          size="large"
          @click="$emit('cancel')"
          :disabled="isUploading"
        >
          <template #icon>
            <close-outlined />
          </template>
          Annulla
        </a-button>

        <!-- Pulsante Chiudi dopo successo/errore -->
        <a-button
          v-if="uploadResult"
          size="large"
          type="primary"
          @click="handleClose"
        >
          <template #icon>
            <check-circle-outlined />
          </template>
          Chiudi
        </a-button>

        <!-- Pulsante Carica Altro dopo successo -->
        <a-button
          v-if="uploadResult?.success"
          size="large"
          @click="resetForm"
        >
          <template #icon>
            <folder-outlined />
          </template>
          Carica Altra Cartella
        </a-button>

        <a-button
          v-if="!uploadResult"
          type="primary"
          size="large"
          @click="handleUpload"
          :disabled="!canUpload || isUploading"
          :loading="isUploading"
        >
          <template #icon v-if="!isUploading">
            <upload-outlined />
          </template>
          {{ isUploading ? 'Caricamento...' : 'Carica Documento' }}
        </a-button>
      </div>
    </a-card>
  </div>
</template>

<script>
import { ref, computed, h } from 'vue'
import axios from 'axios'
import { message } from 'ant-design-vue'
import {
  FolderOutlined,
  UploadOutlined,
  InboxOutlined,
  FileZipOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  FileTextOutlined,
  FileOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'FolderUpload',
  components: {
    FolderOutlined,
    UploadOutlined,
    InboxOutlined,
    FileZipOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    LoadingOutlined,
    FileTextOutlined,
    FileOutlined
  },
  emits: ['cancel', 'success'],
  setup(props, { emit }) {
    const selectedFile = ref(null)
    const fileList = ref([])
    const isUploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const uploadResult = ref(null)

    const formData = ref({
      logical_id: '',
      title: '',
      description: '',
      conservative_id: '',
      conservative_id_authority: '',
      archive_name: '',
      archive_contact: '',
      document_type: ''
    })

    const canUpload = computed(() => {
      return selectedFile.value !== null &&
             formData.value.logical_id.trim() !== '' &&
             formData.value.title.trim() !== ''
    })

    const beforeUpload = (file) => {
      // Validazione file
      const isZip = file.name.endsWith('.zip')
      if (!isZip) {
        message.error('Puoi caricare solo file ZIP!')
        return false
      }

      const isLt5G = file.size / 1024 / 1024 / 1024 < 5
      if (!isLt5G) {
        message.error('Il file deve essere inferiore a 5GB!')
        return false
      }

      selectedFile.value = file
      uploadResult.value = null
      return false // Previene upload automatico
    }

    const handleFileChange = (info) => {
      // Gestito da beforeUpload
    }

    const handleDrop = (event) => {
      // Gestito da a-upload-dragger
    }

    const clearFiles = () => {
      selectedFile.value = null
      fileList.value = []
      uploadResult.value = null
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    const formatCategory = (category) => {
      const categoryNames = {
        master: 'File Master',
        normalized: 'Normalizzati',
        export_high: 'Esportazione Alta Qualità',
        export_low: 'Esportazione Bassa Qualità',
        metadata: 'Metadati',
        icc: 'Profili ICC',
        logs: 'Log',
        other: 'Altri'
      }
      return categoryNames[category] || category
    }

    const resetForm = () => {
      selectedFile.value = null
      fileList.value = []
      uploadResult.value = null
      uploadProgress.value = 0
      uploadStatus.value = ''
      formData.value = {
        logical_id: '',
        title: '',
        description: '',
        conservative_id: '',
        conservative_id_authority: '',
        archive_name: '',
        archive_contact: '',
        document_type: ''
      }
    }

    const handleClose = () => {
      console.log('[FolderUpload] handleClose called, uploadResult:', uploadResult.value)
      // Emetti evento success se il caricamento è riuscito
      if (uploadResult.value?.success) {
        console.log('[FolderUpload] Emitting success event with data:', {
          document_id: uploadResult.value.document_id,
          logical_id: formData.value.logical_id
        })
        emit('success', {
          document_id: uploadResult.value.document_id,
          logical_id: formData.value.logical_id
        })
      }
      // Reset form prima di chiudere
      resetForm()
      // Chiudi modale
      console.log('[FolderUpload] Emitting cancel event')
      emit('cancel')
    }

    const handleUpload = async () => {
      if (!canUpload.value) return

      isUploading.value = true
      uploadProgress.value = 0
      uploadStatus.value = 'Preparazione caricamento...'
      uploadResult.value = null

      try {
        const token = localStorage.getItem('token')
        if (!token) {
          throw new Error('Non autenticato')
        }

        const formDataToSend = new FormData()

        // Caricamento file ZIP
        uploadStatus.value = 'Caricamento archivio ZIP...'
        formDataToSend.append('zip_file', selectedFile.value)

        // Aggiungi metadati
        formDataToSend.append('logical_id', formData.value.logical_id)
        formDataToSend.append('title', formData.value.title)
        if (formData.value.description) formDataToSend.append('description', formData.value.description)
        if (formData.value.conservative_id) formDataToSend.append('conservative_id', formData.value.conservative_id)
        if (formData.value.conservative_id_authority) formDataToSend.append('conservative_id_authority', formData.value.conservative_id_authority)
        if (formData.value.archive_name) formDataToSend.append('archive_name', formData.value.archive_name)
        if (formData.value.archive_contact) formDataToSend.append('archive_contact', formData.value.archive_contact)
        if (formData.value.document_type) formDataToSend.append('document_type', formData.value.document_type)

        uploadStatus.value = 'Caricamento sul server...'

        // Upload
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/upload-folder`,
          formDataToSend,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              uploadProgress.value = percentCompleted
            }
          }
        )

        uploadProgress.value = 100
        uploadStatus.value = 'Caricamento completato!'

        uploadResult.value = {
          success: true,
          message: response.data.message || 'Cartella caricata con successo!',
          categorized_files: response.data.categorized_files,
          total_files: response.data.total_files,
          document_id: response.data.document_id
        }

        message.success('Documento caricato con successo!')

      } catch (error) {
        console.error('Errore caricamento:', error)
        uploadResult.value = {
          success: false,
          message: 'Caricamento fallito',
          error: error.response?.data?.detail || error.message
        }
        message.error('Errore durante il caricamento')
      } finally {
        isUploading.value = false
      }
    }

    return {
      h, // Expose h for template
      selectedFile,
      fileList,
      isUploading,
      uploadProgress,
      uploadStatus,
      uploadResult,
      formData,
      canUpload,
      beforeUpload,
      handleFileChange,
      handleDrop,
      clearFiles,
      formatFileSize,
      formatCategory,
      handleUpload,
      resetForm,
      handleClose,
      // Icons
      FolderOutlined,
      UploadOutlined,
      InboxOutlined,
      FileZipOutlined,
      CheckCircleOutlined,
      CloseCircleOutlined,
      LoadingOutlined,
      FileTextOutlined,
      FileOutlined
    }
  }
}
</script>

<style scoped>
.folder-upload-container {
  max-width: 900px;
  margin: 0 auto;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 8px 0;
}

.form-header p {
  font-size: 16px;
  color: #8c8c8c;
  margin: 0;
}

.upload-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
}

:deep(.ant-upload-drag) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.ant-upload-drag:hover) {
  border-color: #1890ff;
}

:deep(.ant-form-item-label > label) {
  font-weight: 500;
  font-size: 14px;
}

:deep(.ant-descriptions-title) {
  font-weight: 600;
  color: #262626;
  margin-bottom: 16px;
}

:deep(.ant-result-title) {
  font-size: 20px;
  font-weight: 600;
}

:deep(.ant-result-subtitle) {
  font-size: 14px;
  color: #8c8c8c;
}

:deep(.ant-divider-inner-text) {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}
</style>
