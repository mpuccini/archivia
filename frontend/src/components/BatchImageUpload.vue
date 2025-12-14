<template>
  <div class="batch-image-upload">
    <!-- Intestazione -->
    <div class="form-header">
      <picture-outlined :style="{ fontSize: '32px', color: '#722ed1', marginBottom: '16px' }" />
      <h1>Caricamento Batch Immagini</h1>
      <p>Carica più immagini contemporaneamente con associazione automatica ai documenti</p>
    </div>

    <!-- Loading Overlay -->
    <a-spin :spinning="isUploading" tip="Caricamento immagini in corso...">
      <a-card :bordered="false" class="upload-card">
        <!-- Istruzioni -->
        <a-alert
          message="Come funziona il caricamento batch"
          type="info"
          show-icon
          style="margin-bottom: 24px"
        >
          <template #icon>
            <inbox-outlined />
          </template>
          <template #description>
            <div>
              <p>Le immagini verranno automaticamente associate ai documenti in base al nome file = logical_id.</p>
              <p style="margin-top: 8px;"><strong>Esempio:</strong> "DOC001.jpg" verrà associato al documento con logical_id "DOC001".</p>
              <p style="margin-top: 8px;">Se non viene trovato un documento corrispondente, verrà creato automaticamente un nuovo documento.</p>
            </div>
          </template>
        </a-alert>

        <!-- Area di Upload Drag & Drop -->
        <a-upload-dragger
          v-model:file-list="fileList"
          name="images"
          accept=".jpg,.jpeg,.png,.tiff,.tif,.pdf"
          :multiple="true"
          :before-upload="beforeUpload"
          :show-upload-list="false"
          @change="handleFileChange"
          @drop="handleDrop"
        >
          <p class="ant-upload-drag-icon">
            <inbox-outlined :style="{ fontSize: '48px', color: '#722ed1' }" />
          </p>
          <p class="ant-upload-text" style="font-size: 16px; font-weight: 500;">
            Trascina le immagini qui o clicca per sfogliare
          </p>
          <p class="ant-upload-hint" style="color: #8c8c8c;">
            Supporta JPG, PNG, TIFF, PDF fino a 50MB ciascuno
          </p>
        </a-upload-dragger>

        <!-- Lista File Selezionati -->
        <div v-if="files.length > 0" style="margin-top: 24px;">
          <a-card :bordered="false" style="background-color: #f5f5f5;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
              <h3 style="margin: 0; font-size: 16px; font-weight: 600;">
                <file-image-outlined style="margin-right: 8px;" />
                File Selezionati ({{ files.length }})
              </h3>
            </div>

            <!-- Tabella File -->
            <a-table
              :columns="tableColumns"
              :data-source="filesWithStatus"
              :pagination="{ pageSize: 10 }"
              :scroll="{ x: 800 }"
              size="small"
            >
              <template #bodyCell="{ column, record, index }">
                <template v-if="column.key === 'filename'">
                  <div style="display: flex; align-items: center;">
                    <file-image-outlined style="margin-right: 8px; color: #722ed1;" />
                    <span style="font-weight: 500;">{{ record.name }}</span>
                  </div>
                </template>
                <template v-else-if="column.key === 'size'">
                  {{ formatFileSize(record.size) }}
                </template>
                <template v-else-if="column.key === 'status'">
                  <a-tag v-if="record.matchStatus.found" color="success">
                    <template #icon>
                      <link-outlined />
                    </template>
                    Associato a {{ record.matchStatus.logicalId }}
                  </a-tag>
                  <a-tag v-else color="warning">
                    <template #icon>
                      <check-circle-outlined />
                    </template>
                    Nuovo documento
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'actions'">
                  <a-button
                    type="text"
                    danger
                    size="small"
                    @click="removeFile(index)"
                  >
                    <template #icon>
                      <close-circle-outlined />
                    </template>
                  </a-button>
                </template>
              </template>
            </a-table>
          </a-card>
        </div>

        <!-- Conflitti -->
        <div v-if="conflicts.length > 0" style="margin-top: 24px;">
          <a-alert
            message="Risolvi Conflitti"
            type="error"
            show-icon
            style="margin-bottom: 16px"
          >
            <template #icon>
              <exclamation-circle-outlined />
            </template>
            <template #description>
              Sono stati rilevati file multipli con lo stesso logical_id. Scegli come gestirli.
            </template>
          </a-alert>

          <a-collapse v-model:activeKey="activeConflictKeys" style="margin-bottom: 16px;">
            <a-collapse-panel
              v-for="conflict in conflicts"
              :key="conflict.logical_id"
              :header="`Conflitto: ${conflict.logical_id} (${conflict.files.length} file)`"
            >
              <template #extra>
                <close-circle-outlined style="color: #ff4d4f;" />
              </template>

              <a-alert
                :message="conflict.message"
                type="warning"
                show-icon
                style="margin-bottom: 16px"
              />

              <a-radio-group v-model:value="conflict.resolution" style="display: flex; flex-direction: column; gap: 8px;">
                <a-radio value="keep">
                  Mantieni l'immagine esistente
                </a-radio>
                <a-radio value="replace">
                  Sostituisci con la nuova immagine
                </a-radio>
                <a-radio v-if="conflict.type === 'multiple'" value="choose">
                  Fammi scegliere quale file usare
                </a-radio>
              </a-radio-group>

              <!-- Lista file nel conflitto -->
              <div v-if="conflict.files" style="margin-top: 16px;">
                <a-divider orientation="left" style="margin: 16px 0;">File in conflitto</a-divider>
                <a-list
                  :data-source="conflict.files"
                  size="small"
                  bordered
                >
                  <template #renderItem="{ item }">
                    <a-list-item>
                      <a-list-item-meta>
                        <template #title>
                          <file-image-outlined style="margin-right: 8px;" />
                          {{ item.name }}
                        </template>
                        <template #description>
                          {{ formatFileSize(item.size) }}
                        </template>
                      </a-list-item-meta>
                    </a-list-item>
                  </template>
                </a-list>
              </div>
            </a-collapse-panel>
          </a-collapse>
        </div>

        <!-- Statistiche -->
        <div v-if="files.length > 0 && !isUploading" style="margin-top: 24px;">
          <a-row :gutter="16">
            <a-col :span="8">
              <a-card>
                <a-statistic
                  title="Totale File"
                  :value="files.length"
                  :value-style="{ color: '#722ed1' }"
                >
                  <template #prefix>
                    <file-image-outlined />
                  </template>
                </a-statistic>
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card>
                <a-statistic
                  title="Da Associare"
                  :value="matchedCount"
                  :value-style="{ color: '#52c41a' }"
                >
                  <template #prefix>
                    <link-outlined />
                  </template>
                </a-statistic>
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card>
                <a-statistic
                  title="Nuovi Documenti"
                  :value="unmatchedCount"
                  :value-style="{ color: '#faad14' }"
                >
                  <template #prefix>
                    <check-circle-outlined />
                  </template>
                </a-statistic>
              </a-card>
            </a-col>
          </a-row>
        </div>

        <!-- Risultati -->
        <div v-if="uploadResults && !isUploading" style="margin-top: 24px;">
          <!-- Successo completo -->
          <a-result
            v-if="uploadResults.errors.length === 0"
            status="success"
            title="Caricamento Completato con Successo!"
            :sub-title="`${uploadResults.success.length} immagini sono state caricate correttamente.`"
          >
            <template #icon>
              <check-circle-outlined />
            </template>
          </a-result>

          <!-- Successo parziale -->
          <a-result
            v-else-if="uploadResults.success.length > 0"
            status="warning"
            title="Caricamento Completato Parzialmente"
            :sub-title="`${uploadResults.success.length} immagini caricate, ${uploadResults.errors.length} errori.`"
          >
            <template #icon>
              <exclamation-circle-outlined />
            </template>
          </a-result>

          <!-- Fallimento -->
          <a-result
            v-else
            status="error"
            title="Caricamento Fallito"
            :sub-title="`Nessuna immagine è stata caricata. ${uploadResults.errors.length} errori riscontrati.`"
          >
            <template #icon>
              <close-circle-outlined />
            </template>
          </a-result>

          <!-- Statistiche Risultati -->
          <a-row :gutter="16" style="margin: 32px 0;" v-if="uploadResults.success.length > 0 || uploadResults.errors.length > 0">
            <a-col :span="12">
              <a-card>
                <a-statistic
                  title="Immagini Caricate"
                  :value="uploadResults.success.length"
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
                  :value="uploadResults.errors.length"
                  :value-style="{ color: '#ff4d4f' }"
                >
                  <template #prefix>
                    <close-circle-outlined />
                  </template>
                </a-statistic>
              </a-card>
            </a-col>
          </a-row>

          <!-- Dettagli Successi -->
          <a-collapse v-if="uploadResults.success.length > 0" style="margin-bottom: 16px;">
            <a-collapse-panel key="success" header="Immagini Caricate con Successo">
              <template #extra>
                <check-circle-outlined style="color: #52c41a;" />
              </template>
              <a-list
                :data-source="uploadResults.success"
                size="small"
                :pagination="{ pageSize: 5 }"
              >
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        <check-circle-outlined style="color: #52c41a; margin-right: 8px;" />
                        {{ item.filename || item.logical_id }}
                      </template>
                      <template #description>
                        {{ item.message || `Associato al documento ${item.logical_id}` }}
                      </template>
                    </a-list-item-meta>
                  </a-list-item>
                </template>
              </a-list>
            </a-collapse-panel>
          </a-collapse>

          <!-- Dettagli Errori -->
          <a-collapse v-if="uploadResults.errors.length > 0" style="margin-bottom: 16px;">
            <a-collapse-panel key="errors" header="Errori di Caricamento">
              <template #extra>
                <close-circle-outlined style="color: #ff4d4f;" />
              </template>
              <a-list
                :data-source="uploadResults.errors"
                size="small"
                :pagination="{ pageSize: 5 }"
              >
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        <close-circle-outlined style="color: #ff4d4f; margin-right: 8px;" />
                        {{ item.filename || item.logical_id }}
                      </template>
                      <template #description>
                        {{ item.error || item.message }}
                      </template>
                    </a-list-item-meta>
                  </a-list-item>
                </template>
              </a-list>
            </a-collapse-panel>
          </a-collapse>
        </div>

        <!-- Pulsanti Azione -->
        <div style="display: flex; justify-content: space-between; margin-top: 24px;">
          <a-button
            size="large"
            @click="$emit('cancel')"
            :disabled="isUploading"
          >
            <template #icon>
              <close-outlined />
            </template>
            {{ uploadResults ? 'Chiudi' : 'Annulla' }}
          </a-button>
          <a-button
            v-if="!uploadResults"
            type="primary"
            size="large"
            @click="uploadImages"
            :disabled="!canUpload"
            :loading="isUploading"
          >
            <template #icon v-if="!isUploading">
              <upload-outlined />
            </template>
            {{ isUploading ? 'Caricamento...' : `Carica ${files.length} Immagini` }}
          </a-button>
          <a-button
            v-else
            type="primary"
            size="large"
            @click="$emit('upload-complete')"
          >
            <template #icon>
              <check-circle-outlined />
            </template>
            Completa
          </a-button>
        </div>
      </a-card>
    </a-spin>
  </div>
</template>

<script>
import { ref, computed, onMounted, h } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import { message } from 'ant-design-vue'
import {
  PictureOutlined,
  UploadOutlined,
  InboxOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CloseOutlined,
  FileImageOutlined,
  LinkOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'BatchImageUpload',
  components: {
    PictureOutlined,
    UploadOutlined,
    InboxOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    CloseOutlined,
    FileImageOutlined,
    LinkOutlined,
    ExclamationCircleOutlined
  },
  emits: ['upload-complete', 'cancel'],
  setup(props, { emit }) {
    const authStore = useAuthStore()

    const isUploading = ref(false)
    const files = ref([])
    const fileList = ref([])
    const conflicts = ref([])
    const activeConflictKeys = ref([])
    const availableDocuments = ref([])
    const uploadResults = ref(null)

    // Colonne tabella
    const tableColumns = [
      {
        title: 'Nome File',
        key: 'filename',
        width: 300,
        fixed: 'left'
      },
      {
        title: 'Dimensione',
        key: 'size',
        width: 120
      },
      {
        title: 'Stato Associazione',
        key: 'status',
        width: 250
      },
      {
        title: 'Azioni',
        key: 'actions',
        width: 80,
        fixed: 'right'
      }
    ]

    const canUpload = computed(() => {
      return files.value.length > 0 && conflicts.value.every(c => c.resolution)
    })

    const filesWithStatus = computed(() => {
      return files.value.map(file => ({
        ...file,
        matchStatus: getMatchStatus(file)
      }))
    })

    const matchedCount = computed(() => {
      return filesWithStatus.value.filter(f => f.matchStatus.found).length
    })

    const unmatchedCount = computed(() => {
      return filesWithStatus.value.filter(f => !f.matchStatus.found).length
    })

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const isValidImageFile = (file) => {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'application/pdf']
      const validExtensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.pdf']

      return validTypes.includes(file.type) ||
             validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))
    }

    const extractLogicalIdFromFilename = (filename) => {
      // Rimuovi l'estensione del file e restituisci il nome base
      return filename.replace(/\.[^/.]+$/, '')
    }

    const getMatchStatus = (file) => {
      const logicalId = extractLogicalIdFromFilename(file.name)
      const document = availableDocuments.value.find(d => d.logical_id === logicalId)

      if (document) {
        return { found: true, logicalId, document }
      } else {
        return { found: false, logicalId, document: null }
      }
    }

    const beforeUpload = (file) => {
      if (!isValidImageFile(file)) {
        message.error(`${file.name} non è un file immagine valido`)
        return false
      }

      if (file.size > 50 * 1024 * 1024) {
        message.error(`${file.name} supera il limite di 50MB`)
        return false
      }

      // Controlla duplicati
      const isDuplicate = files.value.some(f => f.name === file.name)
      if (isDuplicate) {
        message.warning(`${file.name} è già stato aggiunto`)
        return false
      }

      files.value.push(file)
      checkForConflicts()
      return false // Previene upload automatico
    }

    const handleFileChange = (info) => {
      // Gestito da beforeUpload
    }

    const handleDrop = (e) => {
      // Gestito da a-upload-dragger
    }

    const removeFile = (index) => {
      files.value.splice(index, 1)
      fileList.value.splice(index, 1)
      checkForConflicts()

      if (files.value.length === 0) {
        uploadResults.value = null
      }
    }

    const checkForConflicts = () => {
      conflicts.value = []
      activeConflictKeys.value = []

      // Raggruppa file per logical_id
      const fileGroups = {}
      files.value.forEach(file => {
        const logicalId = extractLogicalIdFromFilename(file.name)
        if (!fileGroups[logicalId]) {
          fileGroups[logicalId] = []
        }
        fileGroups[logicalId].push(file)
      })

      // Controlla file multipli con lo stesso logical_id
      Object.entries(fileGroups).forEach(([logicalId, groupFiles]) => {
        if (groupFiles.length > 1) {
          const conflict = {
            logical_id: logicalId,
            type: 'multiple',
            message: `Trovati ${groupFiles.length} file per ${logicalId}: ${groupFiles.map(f => f.name).join(', ')}`,
            resolution: 'choose',
            files: groupFiles
          }
          conflicts.value.push(conflict)
          activeConflictKeys.value.push(logicalId)
        }
      })
    }

    const loadAvailableDocuments = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents`, {
          params: { size: 1000 }, // Recupera tutti i documenti
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })

        availableDocuments.value = response.data.documents || response.data.items || response.data
      } catch (error) {
        console.error('Errore nel caricamento dei documenti:', error)
        message.error('Impossibile caricare l\'elenco dei documenti')
      }
    }

    const uploadImages = async () => {
      if (!canUpload.value) {
        message.warning('Risolvi tutti i conflitti prima di caricare')
        return
      }

      isUploading.value = true
      uploadResults.value = null

      try {
        const formData = new FormData()

        files.value.forEach(file => {
          formData.append('files', file)
        })

        // Aggiungi risoluzioni conflitti
        conflicts.value.forEach(conflict => {
          formData.append(`conflict_${conflict.logical_id}`, conflict.resolution)
        })

        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/images/batch`,
          formData,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'multipart/form-data'
            }
          }
        )

        uploadResults.value = response.data

        // Mostra messaggi di risultato
        if (response.data.errors && response.data.errors.length === 0) {
          message.success(`Tutte le ${response.data.success.length} immagini sono state caricate con successo!`)
        } else if (response.data.success && response.data.success.length > 0) {
          message.warning(`${response.data.success.length} immagini caricate, ${response.data.errors.length} errori`)
        } else {
          message.error('Nessuna immagine è stata caricata a causa di errori')
        }

      } catch (error) {
        console.error('Errore durante il caricamento delle immagini:', error)
        message.error('Errore durante il caricamento: ' + (error.response?.data?.detail || error.message))

        // Crea risultato errore
        uploadResults.value = {
          success: [],
          errors: [{
            filename: 'Generale',
            error: error.response?.data?.detail || error.message
          }]
        }
      } finally {
        isUploading.value = false
      }
    }

    onMounted(() => {
      loadAvailableDocuments()
    })

    return {
      h,
      isUploading,
      files,
      fileList,
      conflicts,
      activeConflictKeys,
      uploadResults,
      canUpload,
      filesWithStatus,
      matchedCount,
      unmatchedCount,
      tableColumns,
      formatFileSize,
      beforeUpload,
      handleFileChange,
      handleDrop,
      removeFile,
      uploadImages
    }
  }
}
</script>

<style scoped>
.batch-image-upload {
  padding: 24px;
  max-width: 1200px;
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

.upload-card {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02);
}

:deep(.ant-upload-drag) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.ant-upload-drag:hover) {
  border-color: #722ed1;
}

:deep(.ant-table-small) {
  font-size: 13px;
}

:deep(.ant-statistic-title) {
  font-size: 14px;
  color: #8c8c8c;
}

:deep(.ant-statistic-content) {
  font-size: 24px;
  font-weight: 600;
}

:deep(.ant-collapse-header) {
  font-weight: 500;
}

:deep(.ant-result-title) {
  font-size: 20px;
  font-weight: 600;
}

:deep(.ant-result-subtitle) {
  font-size: 14px;
  color: #8c8c8c;
}
</style>
