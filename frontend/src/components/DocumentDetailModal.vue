<template>
  <div v-if="document" class="document-detail-modal">
    <!-- Header with Actions -->
    <div class="flex items-center justify-between mb-4 pb-4 border-b">
      <div>
        <h3 class="text-2xl font-bold text-gray-900">
          {{ document?.title || document?.logical_id || 'Dettagli Documento' }}
        </h3>
        <p class="mt-1 text-sm text-gray-600">
          <span class="font-medium">ID:</span> {{ document?.logical_id }}
        </p>
      </div>
      <a-space>
        <a-button v-if="!isEditing" type="primary" @click="startEdit">
          <template #icon><EditOutlined /></template>
          Modifica
        </a-button>

        <template v-if="isEditing">
          <a-button type="primary" @click="saveChanges" :loading="saving">
            <template #icon><SaveOutlined /></template>
            Salva
          </a-button>
          <a-button danger @click="deleteDocument" :loading="deleting">
            <template #icon><DeleteOutlined /></template>
            Elimina
          </a-button>
          <a-button @click="cancelEdit" :disabled="saving || deleting">
            <template #icon><CloseOutlined /></template>
            Annulla
          </a-button>
        </template>

        <a-button type="text" @click="closeModal">
          <template #icon><CloseOutlined /></template>
          Chiudi
        </a-button>
      </a-space>
    </div>

    <!-- Tabs -->
    <a-tabs v-model:activeKey="activeTab" size="large">
      <!-- Overview Tab -->
      <a-tab-pane key="overview" tab="Panoramica">
        <template #tab>
          <span>
            <InfoCircleOutlined />
            Panoramica
          </span>
        </template>

        <div class="overflow-y-auto" style="max-height: 500px;">
          <!-- Display Mode -->
          <a-descriptions v-if="!isEditing" bordered :column="1" size="small">
            <a-descriptions-item label="ID Logico" v-if="document?.logical_id">
              {{ document.logical_id }}
            </a-descriptions-item>
            <a-descriptions-item label="ID Conservativo" v-if="document?.conservative_id">
              {{ document.conservative_id }}
            </a-descriptions-item>
            <a-descriptions-item label="Autorità ID" v-if="document?.conservative_id_authority">
              {{ document.conservative_id_authority }}
            </a-descriptions-item>
            <a-descriptions-item label="Titolo" v-if="document?.title">
              {{ document.title }}
            </a-descriptions-item>
            <a-descriptions-item label="Descrizione" v-if="document?.description">
              {{ document.description }}
            </a-descriptions-item>
            <a-descriptions-item label="Tipo" v-if="document?.document_type">
              {{ document.document_type }}
            </a-descriptions-item>
            <a-descriptions-item label="Pagine Totali" v-if="document?.total_pages">
              {{ document.total_pages }}
            </a-descriptions-item>
            <a-descriptions-item label="Data Creazione" v-if="document?.created_at">
              {{ formatDate(document.created_at) }}
            </a-descriptions-item>
          </a-descriptions>

          <!-- Edit Mode -->
          <a-form v-else :model="editForm" layout="vertical" class="space-y-6">
            <!-- Image Upload Section -->
            <a-card title="🖼️ Immagine Documento" size="small" class="mb-6">
              <a-upload-dragger
                :before-upload="validateAndSetImage"
                :show-upload-list="false"
                accept="image/jpeg,image/png,image/tiff"
                @drop="handleImageDrop"
              >
                <p class="ant-upload-drag-icon">
                  <UploadOutlined style="font-size: 48px; color: #1890ff;" />
                </p>
                <p class="ant-upload-text">Clicca o trascina un'immagine qui per caricare</p>
                <p class="ant-upload-hint">
                  Formati supportati: JPEG, PNG, TIFF (max 50MB)
                </p>
              </a-upload-dragger>

              <div v-if="imageUploading" class="mt-4">
                <a-progress :percent="imageUploadProgress" status="active" />
                <p class="text-sm text-gray-600 mt-2">Caricamento in corso...</p>
              </div>

              <div v-if="imageFiles.length > 0" class="mt-4">
                <p class="text-sm text-gray-600 mb-2">Immagine corrente:</p>
                <a-tag color="blue">{{ imageFiles[0].filename }}</a-tag>
              </div>
            </a-card>

            <!-- Basic Information -->
            <a-card title="Informazioni di Base" size="small">
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="ID Logico" required>
                    <a-input v-model:value="editForm.logical_id" placeholder="Inserisci ID logico" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="ID Conservativo">
                    <a-input v-model:value="editForm.conservative_id" placeholder="es. IT-MO0172-DOC001" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-form-item label="Autorità ID">
                <a-input v-model:value="editForm.conservative_id_authority" placeholder="es. IT-MO0172" />
              </a-form-item>

              <a-form-item label="Titolo">
                <a-input v-model:value="editForm.title" placeholder="Inserisci titolo" />
              </a-form-item>

              <a-form-item label="Descrizione">
                <a-textarea v-model:value="editForm.description" :rows="4" placeholder="Inserisci descrizione" />
              </a-form-item>

              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="Tipo di Documento">
                    <a-select v-model:value="editForm.document_type" placeholder="Seleziona tipo">
                      <a-select-option value="manuscript">Manoscritto</a-select-option>
                      <a-select-option value="letter">Lettera</a-select-option>
                      <a-select-option value="book">Libro</a-select-option>
                      <a-select-option value="map">Mappa</a-select-option>
                      <a-select-option value="photograph">Fotografia</a-select-option>
                      <a-select-option value="other">Altro</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="Pagine Totali">
                    <a-input-number v-model:value="editForm.total_pages" :min="0" style="width: 100%;" />
                  </a-form-item>
                </a-col>
              </a-row>
            </a-card>

            <!-- Archive Information -->
            <a-card title="Informazioni Archivio" size="small">
              <a-form-item label="Nome Archivio">
                <a-input v-model:value="editForm.archive_name" placeholder="es. Archivio di Stato di Modena" />
              </a-form-item>

              <a-form-item label="Contatto Archivio">
                <a-input v-model:value="editForm.archive_contact" type="email" placeholder="archivio@example.com" />
              </a-form-item>

              <a-form-item label="Nome Fondo">
                <a-input v-model:value="editForm.fund_name" placeholder="es. Fondo Estense" />
              </a-form-item>

              <a-form-item label="Nome Serie">
                <a-input v-model:value="editForm.series_name" placeholder="es. Serie Amministrativa" />
              </a-form-item>

              <a-form-item label="Numero Fascicolo/Unità">
                <a-input v-model:value="editForm.folder_number" placeholder="es. Busta 45" />
              </a-form-item>
            </a-card>

            <!-- Temporal & Contextual -->
            <a-card title="Informazioni Temporali e Contestuali" size="small">
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="Data Da">
                    <a-date-picker v-model:value="editForm.date_from" format="YYYY-MM-DD" style="width: 100%;" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="Data A">
                    <a-date-picker v-model:value="editForm.date_to" format="YYYY-MM-DD" style="width: 100%;" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-form-item label="Periodo Storico">
                <a-input v-model:value="editForm.period" placeholder="es. Risorgimento" />
              </a-form-item>

              <a-form-item label="Luogo">
                <a-input v-model:value="editForm.location" placeholder="es. Modena, Italia" />
              </a-form-item>

              <a-form-item label="Lingua">
                <a-select v-model:value="editForm.language" placeholder="Seleziona lingua">
                  <a-select-option value="it">Italiano</a-select-option>
                  <a-select-option value="en">Inglese</a-select-option>
                  <a-select-option value="fr">Francese</a-select-option>
                  <a-select-option value="de">Tedesco</a-select-option>
                  <a-select-option value="es">Spagnolo</a-select-option>
                  <a-select-option value="la">Latino</a-select-option>
                  <a-select-option value="other">Altro</a-select-option>
                </a-select>
              </a-form-item>

              <a-form-item label="Soggetti/Parole Chiave">
                <a-input v-model:value="editForm.subjects" placeholder="Separati da virgola" />
              </a-form-item>
            </a-card>

            <!-- ECO-MiC Metadata -->
            <a-card title="Metadati ECO-MiC 1.2" size="small">
              <a-collapse>
                <a-collapse-panel key="1" header="Tipo di Risorsa e Descrizione Fisica">
                  <a-form-item label="Tipo di Risorsa">
                    <a-select v-model:value="editForm.type_of_resource" placeholder="Seleziona tipo">
                      <a-select-option value="risorsa manoscritta">Risorsa Manoscritta</a-select-option>
                      <a-select-option value="documento testuale">Documento Testuale</a-select-option>
                      <a-select-option value="risorsa cartografica">Risorsa Cartografica</a-select-option>
                      <a-select-option value="immagine fissa">Immagine Fissa</a-select-option>
                    </a-select>
                  </a-form-item>

                  <a-form-item label="Forma Fisica">
                    <a-input v-model:value="editForm.physical_form" />
                  </a-form-item>

                  <a-form-item label="Descrizione Estensione">
                    <a-textarea v-model:value="editForm.extent_description" :rows="2" />
                  </a-form-item>
                </a-collapse-panel>

                <a-collapse-panel key="2" header="Produttore e Creatore">
                  <a-form-item label="Nome Produttore">
                    <a-input v-model:value="editForm.producer_name" />
                  </a-form-item>

                  <a-row :gutter="16">
                    <a-col :span="12">
                      <a-form-item label="Tipo Produttore">
                        <a-select v-model:value="editForm.producer_type">
                          <a-select-option value="corporate">Ente</a-select-option>
                          <a-select-option value="personal">Persona</a-select-option>
                        </a-select>
                      </a-form-item>
                    </a-col>
                    <a-col :span="12">
                      <a-form-item label="Ruolo Produttore">
                        <a-input v-model:value="editForm.producer_role" />
                      </a-form-item>
                    </a-col>
                  </a-row>

                  <a-form-item label="Nome Creatore">
                    <a-input v-model:value="editForm.creator_name" />
                  </a-form-item>

                  <a-row :gutter="16">
                    <a-col :span="12">
                      <a-form-item label="Tipo Creatore">
                        <a-select v-model:value="editForm.creator_type">
                          <a-select-option value="personal">Persona</a-select-option>
                          <a-select-option value="corporate">Ente</a-select-option>
                        </a-select>
                      </a-form-item>
                    </a-col>
                    <a-col :span="12">
                      <a-form-item label="Ruolo Creatore">
                        <a-input v-model:value="editForm.creator_role" />
                      </a-form-item>
                    </a-col>
                  </a-row>
                </a-collapse-panel>

                <a-collapse-panel key="3" header="Diritti">
                  <a-form-item label="Categoria Diritti">
                    <a-select v-model:value="editForm.rights_category">
                      <a-select-option value="COPYRIGHTED">Protetto da Copyright</a-select-option>
                      <a-select-option value="PUBLIC DOMAIN">Pubblico Dominio</a-select-option>
                      <a-select-option value="CONTRACTUAL">Contrattuale</a-select-option>
                      <a-select-option value="OTHER">Altro</a-select-option>
                    </a-select>
                  </a-form-item>

                  <a-form-item label="Titolare Diritti">
                    <a-input v-model:value="editForm.rights_holder" />
                  </a-form-item>

                  <a-form-item label="Vincolo Diritti">
                    <a-input v-model:value="editForm.rights_constraint" placeholder="es. NoC-OKLR" />
                  </a-form-item>

                  <a-form-item label="URL Licenza">
                    <a-input v-model:value="editForm.license_url" type="url" />
                  </a-form-item>

                  <a-form-item label="Dichiarazione Diritti">
                    <a-textarea v-model:value="editForm.rights_statement" :rows="3" />
                  </a-form-item>
                </a-collapse-panel>

                <a-collapse-panel key="4" header="Metadati Tecnici">
                  <a-form-item label="Produttore Immagine">
                    <a-input v-model:value="editForm.image_producer" placeholder="es. EDS Gamma" />
                  </a-form-item>

                  <a-form-item label="Produttore Scanner">
                    <a-input v-model:value="editForm.scanner_manufacturer" />
                  </a-form-item>

                  <a-form-item label="Modello Scanner">
                    <a-input v-model:value="editForm.scanner_model" />
                  </a-form-item>
                </a-collapse-panel>

                <a-collapse-panel key="5" header="Stato Record">
                  <a-form-item label="Stato Record METS">
                    <a-select v-model:value="editForm.record_status">
                      <a-select-option value="COMPLETE">Completo</a-select-option>
                      <a-select-option value="MINIMUM">Minimo</a-select-option>
                      <a-select-option value="REFERENCED">Referenziato</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-collapse-panel>
              </a-collapse>
            </a-card>
          </a-form>
        </div>
      </a-tab-pane>

      <!-- Archive Tab -->
      <a-tab-pane key="archive" tab="Info Archivio">
        <template #tab>
          <span>
            <FolderOpenOutlined />
            Info Archivio
          </span>
        </template>

        <div class="overflow-y-auto" style="max-height: 500px;">
          <a-empty v-if="!hasArchiveInfo" description="Nessuna informazione archivio disponibile" />

          <a-descriptions v-else bordered :column="1" size="small">
            <a-descriptions-item label="Nome Archivio" v-if="document.archive_name">
              {{ document.archive_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Contatto" v-if="document.archive_contact">
              {{ document.archive_contact }}
            </a-descriptions-item>
            <a-descriptions-item label="Nome Fondo" v-if="document.fund_name">
              {{ document.fund_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Nome Serie" v-if="document.series_name">
              {{ document.series_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Numero Fascicolo" v-if="document.folder_number">
              {{ document.folder_number }}
            </a-descriptions-item>
            <a-descriptions-item label="Periodo" v-if="document.period">
              {{ document.period }}
            </a-descriptions-item>
            <a-descriptions-item label="Luogo" v-if="document.location">
              {{ document.location }}
            </a-descriptions-item>
            <a-descriptions-item label="Lingua" v-if="document.language">
              {{ document.language }}
            </a-descriptions-item>
            <a-descriptions-item label="Soggetti" v-if="document.subjects">
              {{ document.subjects }}
            </a-descriptions-item>
            <a-descriptions-item label="Produttore" v-if="document.producer_name">
              {{ document.producer_name }}<span v-if="document.producer_type"> ({{ document.producer_type }})</span>
            </a-descriptions-item>
            <a-descriptions-item label="Creatore" v-if="document.creator_name">
              {{ document.creator_name }}<span v-if="document.creator_type"> ({{ document.creator_type }})</span>
            </a-descriptions-item>
          </a-descriptions>
        </div>
      </a-tab-pane>

      <!-- Files Tab -->
      <a-tab-pane key="files">
        <template #tab>
          <span>
            <FileImageOutlined />
            File ({{ document?.document_files?.length || 0 }})
          </span>
        </template>

        <div class="overflow-y-auto" style="max-height: 500px;">
          <a-empty v-if="!document?.document_files || document.document_files.length === 0" description="Nessun file" />

          <div v-else class="space-y-6">
            <div v-for="(files, category) in filesByCategory" :key="category" class="file-category">
              <h4 class="text-lg font-semibold mb-3 flex items-center gap-2">
                <span>{{ getCategoryIcon(category) }}</span>
                <span>{{ getCategoryLabel(category) }}</span>
                <a-tag color="blue">{{ files.length }}</a-tag>
              </h4>

              <a-row :gutter="[16, 16]">
                <a-col :xs="24" :sm="12" :md="8" v-for="file in files" :key="file.id">
                  <a-card hoverable size="small" @click="selectFile(file)" style="cursor: pointer;">
                    <div class="aspect-square bg-gray-100 rounded mb-2 relative overflow-hidden">
                      <a-spin v-if="loadingThumbnails[file.id]" class="w-full h-full flex items-center justify-center" />
                      <img
                        v-else-if="isImageFile(file) && getFileThumbnail(file)"
                        :src="getFileThumbnail(file)"
                        :alt="file.filename"
                        class="w-full h-full object-cover"
                      />
                      <div v-else class="w-full h-full flex items-center justify-center">
                        <FileOutlined style="font-size: 48px; color: #d9d9d9;" />
                      </div>

                      <a-tag v-if="isDNGFile(file)" color="blue" class="absolute top-2 right-2">
                        <CameraOutlined /> DNG RAW
                      </a-tag>
                    </div>

                    <a-typography-text strong ellipsis class="block mb-1">
                      {{ file.filename }}
                    </a-typography-text>

                    <div class="text-xs text-gray-500 space-y-1">
                      <div v-if="file.scanner_manufacturer">
                        📷 {{ file.scanner_manufacturer }} {{ file.scanner_model_name }}
                      </div>
                      <div>📏 {{ file.image_width }}x{{ file.image_height }}</div>
                      <div>💾 {{ formatFileSize(file.file_size) }}</div>
                    </div>

                    <div class="mt-2 flex gap-2" @click.stop>
                      <a-button type="primary" size="small" block @click="downloadFile(file)">
                        <template #icon><DownloadOutlined /></template>
                        Scarica
                      </a-button>
                      <a-button danger size="small" @click="deleteFile(file)" :loading="deletingFileId === file.id">
                        <template #icon><DeleteOutlined /></template>
                      </a-button>
                    </div>
                  </a-card>
                </a-col>
              </a-row>
            </div>
          </div>
        </div>
      </a-tab-pane>
    </a-tabs>

    <!-- File Detail Modal -->
    <a-modal
      v-model:open="showFileDetail"
      title="Dettagli File"
      :footer="null"
      :width="1000"
      @cancel="closeFileDetail"
    >
      <div v-if="selectedFile" class="grid grid-cols-2 gap-6">
        <!-- Image Preview -->
        <div>
          <div class="bg-gray-100 rounded-lg p-4 aspect-square flex items-center justify-center">
            <img
              v-if="isImageFile(selectedFile) && imageDataUrl"
              :src="imageDataUrl"
              :alt="selectedFile.filename"
              class="max-w-full max-h-full object-contain cursor-pointer"
              @click="showImageViewer = true"
            />
            <FileOutlined v-else style="font-size: 64px; color: #d9d9d9;" />
          </div>
          <p v-if="isDNGFile(selectedFile)" class="text-xs text-gray-500 mt-2">
            ℹ️ Anteprima generata automaticamente dal file DNG
          </p>
        </div>

        <!-- Metadata -->
        <div class="space-y-4 overflow-y-auto" style="max-height: 500px;">
          <a-descriptions title="Informazioni Base" bordered :column="1" size="small">
            <a-descriptions-item label="Nome File">{{ selectedFile.filename }}</a-descriptions-item>
            <a-descriptions-item label="Dimensione">{{ formatFileSize(selectedFile.file_size) }}</a-descriptions-item>
            <a-descriptions-item label="Formato">{{ selectedFile.content_type }}</a-descriptions-item>
            <a-descriptions-item label="MD5">{{ selectedFile.md5_checksum }}</a-descriptions-item>
            <a-descriptions-item label="Risoluzione" v-if="selectedFile.image_width">
              {{ selectedFile.image_width }} x {{ selectedFile.image_height }}
            </a-descriptions-item>
          </a-descriptions>

          <a-descriptions v-if="hasMetadata(selectedFile)" title="Metadati Tecnici (MIX)" bordered :column="1" size="small">
            <a-descriptions-item label="Formato" v-if="selectedFile.format_name">
              {{ selectedFile.format_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Spazio Colore" v-if="selectedFile.color_space">
              {{ selectedFile.color_space }}
            </a-descriptions-item>
            <a-descriptions-item label="Bit per Campione" v-if="selectedFile.bits_per_sample">
              {{ selectedFile.bits_per_sample }}
            </a-descriptions-item>
            <a-descriptions-item label="Campioni per Pixel" v-if="selectedFile.samples_per_pixel">
              {{ selectedFile.samples_per_pixel }}
            </a-descriptions-item>
            <a-descriptions-item label="Compressione" v-if="selectedFile.compression_scheme">
              {{ selectedFile.compression_scheme }}
            </a-descriptions-item>
            <a-descriptions-item label="DPI" v-if="selectedFile.x_sampling_frequency">
              {{ selectedFile.x_sampling_frequency }} x {{ selectedFile.y_sampling_frequency }}
              <span v-if="selectedFile.sampling_frequency_unit"> {{ selectedFile.sampling_frequency_unit }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="Byte Order" v-if="selectedFile.byte_order">
              {{ selectedFile.byte_order }}
            </a-descriptions-item>
            <a-descriptions-item label="Orientamento" v-if="selectedFile.orientation">
              {{ selectedFile.orientation }}
            </a-descriptions-item>
            <a-descriptions-item label="Profilo ICC" v-if="selectedFile.icc_profile_name">
              {{ selectedFile.icc_profile_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Data Creazione" v-if="selectedFile.date_time_created">
              {{ formatDate(selectedFile.date_time_created) }}
            </a-descriptions-item>
          </a-descriptions>

          <a-descriptions v-if="hasCameraMetadata(selectedFile)" title="Info Fotocamera/Scanner" bordered :column="1" size="small">
            <a-descriptions-item label="Produttore" v-if="selectedFile.scanner_manufacturer">
              {{ selectedFile.scanner_manufacturer }}
            </a-descriptions-item>
            <a-descriptions-item label="Modello" v-if="selectedFile.scanner_model_name">
              {{ selectedFile.scanner_model_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Software" v-if="selectedFile.scanning_software_name">
              {{ selectedFile.scanning_software_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Versione Software" v-if="selectedFile.scanning_software_version">
              {{ selectedFile.scanning_software_version }}
            </a-descriptions-item>
          </a-descriptions>
        </div>
      </div>
    </a-modal>

    <!-- Image Viewer Modal -->
    <a-modal
      v-model:open="showImageViewer"
      title="Visualizzatore Immagine"
      :footer="null"
      :width="1400"
      centered
    >
      <div class="bg-black rounded p-4" style="max-height: 80vh;">
        <img
          v-if="imageDataUrl"
          :src="imageDataUrl"
          :alt="selectedFile?.filename"
          class="w-full h-full object-contain"
        />
      </div>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth'
import {
  EditOutlined,
  SaveOutlined,
  DeleteOutlined,
  CloseOutlined,
  InfoCircleOutlined,
  InboxOutlined,
  FileImageOutlined,
  PictureOutlined,
  DownloadOutlined,
  FileOutlined,
  CameraOutlined,
  FolderOpenOutlined,
  UploadOutlined
} from '@ant-design/icons-vue'
import axios from 'axios'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'

export default {
  name: 'DocumentDetailModal',
  components: {
    EditOutlined,
    SaveOutlined,
    DeleteOutlined,
    CloseOutlined,
    InfoCircleOutlined,
    InboxOutlined,
    FileImageOutlined,
    PictureOutlined,
    DownloadOutlined,
    FileOutlined,
    CameraOutlined,
    FolderOpenOutlined,
    UploadOutlined
  },
  props: {
    document: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'updated', 'deleted'],
  setup(props, { emit }) {
    const authStore = useAuthStore()

    // State
    const isEditing = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const selectedFile = ref(null)
    const deletingFileId = ref(null)
    const imageDataUrl = ref('')
    const showImageViewer = ref(false)
    const showFileDetail = ref(false)
    const imageUploading = ref(false)
    const imageUploadProgress = ref(0)
    const activeTab = ref('overview')
    const imageBlobUrls = ref({})
    const loadingFiles = ref(false)
    const loadingThumbnails = ref({})

    // Edit form
    const editForm = reactive({
      logical_id: '',
      conservative_id: '',
      conservative_id_authority: '',
      title: '',
      description: '',
      document_type: '',
      total_pages: null,
      archive_name: '',
      archive_contact: '',
      fund_name: '',
      series_name: '',
      folder_number: '',
      date_from: null,
      date_to: null,
      period: '',
      location: '',
      language: '',
      subjects: '',
      type_of_resource: '',
      physical_form: '',
      extent_description: '',
      producer_name: '',
      producer_type: '',
      producer_role: '',
      creator_name: '',
      creator_type: '',
      creator_role: '',
      rights_category: '',
      rights_holder: '',
      rights_constraint: '',
      license_url: '',
      rights_statement: '',
      image_producer: '',
      scanner_manufacturer: '',
      scanner_model: '',
      record_status: ''
    })

    // Computed
    const imageFiles = computed(() => {
      return props.document?.document_files?.filter(f => isImageFile(f)) || []
    })

    const filesByCategory = computed(() => {
      const files = props.document?.document_files || []
      const grouped = {}

      files.forEach(file => {
        const category = file.file_category || 'other'
        if (!grouped[category]) {
          grouped[category] = []
        }
        grouped[category].push(file)
      })

      return grouped
    })

    const hasArchiveInfo = computed(() => {
      if (!props.document) return false
      return !!(
        props.document.archive_name ||
        props.document.archive_contact ||
        props.document.fund_name ||
        props.document.series_name ||
        props.document.folder_number ||
        props.document.period ||
        props.document.location ||
        props.document.language ||
        props.document.subjects ||
        props.document.producer_name ||
        props.document.creator_name
      )
    })

    // Methods
    const closeModal = () => {
      if (isEditing.value) {
        cancelEdit()
      }
      emit('close')
    }

    const closeFileDetail = () => {
      showFileDetail.value = false
      selectedFile.value = null
      imageDataUrl.value = ''
    }

    const startEdit = () => {
      if (!props.document) return

      // Populate form
      Object.keys(editForm).forEach(key => {
        if (key === 'date_from' || key === 'date_to') {
          editForm[key] = props.document[key] ? dayjs(props.document[key]) : null
        } else {
          editForm[key] = props.document[key] || ''
        }
      })

      isEditing.value = true
    }

    const cancelEdit = () => {
      isEditing.value = false
      Object.keys(editForm).forEach(key => {
        editForm[key] = ''
      })
    }

    const saveChanges = async () => {
      if (!props.document?.id) return

      saving.value = true

      try {
        const payload = { ...editForm }

        // Convert dayjs to string
        if (payload.date_from) {
          payload.date_from = payload.date_from.format('YYYY-MM-DD')
        }
        if (payload.date_to) {
          payload.date_to = payload.date_to.format('YYYY-MM-DD')
        }

        await axios.put(
          `${import.meta.env.VITE_API_URL}/api/documents/${props.document.id}`,
          payload,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          }
        )

        message.success('Documento aggiornato con successo')
        isEditing.value = false
        emit('updated')
      } catch (err) {
        console.error('Error saving document:', err)
        message.error('Errore durante il salvataggio: ' + (err.response?.data?.detail || err.message))
      } finally {
        saving.value = false
      }
    }

    const deleteDocument = async () => {
      if (!props.document?.id) return

      deleting.value = true

      try {
        await axios.delete(
          `${import.meta.env.VITE_API_URL}/api/documents/${props.document.id}`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          }
        )

        message.success('Documento eliminato con successo')
        emit('deleted')
      } catch (err) {
        console.error('Error deleting document:', err)
        message.error('Errore durante l\'eliminazione: ' + (err.response?.data?.detail || err.message))
      } finally {
        deleting.value = false
      }
    }

    const selectFile = async (file) => {
      selectedFile.value = file

      if (isImageFile(file)) {
        await loadImagePreview(file)
      }

      showFileDetail.value = true
    }

    const loadImagePreview = async (file) => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/files/${file.id}/stream`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )

        imageDataUrl.value = URL.createObjectURL(response.data)
      } catch (err) {
        console.error('Error loading image preview:', err)
      }
    }

    const downloadFile = async (file) => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/files/${file.id}/stream`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )

        const blob = new Blob([response.data])
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = file.filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)

        message.success('File scaricato con successo')
      } catch (err) {
        console.error('Error downloading file:', err)
        message.error('Errore durante lo scaricamento del file')
      }
    }

    const deleteFile = async (file) => {
      deletingFileId.value = file.id

      try {
        await axios.delete(
          `${import.meta.env.VITE_API_URL}/api/files/${file.id}`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          }
        )

        message.success('File eliminato con successo')
        emit('updated')
      } catch (err) {
        console.error('Error deleting file:', err)
        message.error('Errore durante l\'eliminazione del file')
      } finally {
        deletingFileId.value = null
      }
    }

    const validateAndSetImage = (file) => {
      const isValidType = ['image/jpeg', 'image/png', 'image/tiff'].includes(file.type)
      if (!isValidType) {
        message.error('Formato non supportato. Usa JPEG, PNG o TIFF')
        return false
      }

      const isValidSize = file.size / 1024 / 1024 < 50
      if (!isValidSize) {
        message.error('Il file deve essere più piccolo di 50MB')
        return false
      }

      uploadImage(file)
      return false // Prevent auto upload
    }

    const uploadImage = async (file) => {
      if (!props.document?.id) return

      imageUploading.value = true
      imageUploadProgress.value = 0

      const formData = new FormData()
      formData.append('file', file)
      formData.append('document_id', props.document.id)

      try {
        await axios.post(
          `${import.meta.env.VITE_API_URL}/api/files/upload-image`,
          formData,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              imageUploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            }
          }
        )

        message.success('Immagine caricata con successo')
        emit('updated')
      } catch (err) {
        console.error('Error uploading image:', err)
        message.error('Errore durante il caricamento dell\'immagine')
      } finally {
        imageUploading.value = false
        imageUploadProgress.value = 0
      }
    }

    const handleImageDrop = (e) => {
      const files = e.dataTransfer.files
      if (files.length > 0) {
        validateAndSetImage(files[0])
      }
    }

    const loadAllImagePreviews = async () => {
      loadingFiles.value = true
      const files = imageFiles.value

      for (const file of files) {
        if (!imageBlobUrls.value[file.id]) {
          loadingThumbnails.value[file.id] = true
          try {
            const response = await axios.get(
              `${import.meta.env.VITE_API_URL}/api/files/${file.id}/stream`,
              {
                headers: {
                  'Authorization': `Bearer ${authStore.token}`
                },
                responseType: 'blob'
              }
            )

            imageBlobUrls.value[file.id] = URL.createObjectURL(response.data)
          } catch (err) {
            console.error('Error loading thumbnail:', err)
          } finally {
            loadingThumbnails.value[file.id] = false
          }
        }
      }

      loadingFiles.value = false
    }

    const getFileThumbnail = (file) => {
      return imageBlobUrls.value[file.id] || null
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return dayjs(dateString).format('YYYY-MM-DD')
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const isImageFile = (file) => {
      // Escludi file testuali anche se hanno content_type image/*
      const textExtensions = ['.xml', '.csv', '.txt', '.log', '.json', '.html', '.css', '.js']
      const hasTextExtension = textExtensions.some(ext => file.filename?.toLowerCase().endsWith(ext))

      if (hasTextExtension) {
        return false
      }

      return file.content_type?.startsWith('image/')
    }

    const isDNGFile = (file) => {
      return file.content_type === 'image/x-adobe-dng' || file.filename?.toLowerCase().endsWith('.dng')
    }

    const hasMetadata = (file) => {
      return file.color_space ||
             file.bits_per_sample ||
             file.x_sampling_frequency ||
             file.samples_per_pixel ||
             file.compression_scheme ||
             file.sampling_frequency_unit ||
             file.format_name ||
             file.byte_order ||
             file.orientation ||
             file.icc_profile_name
    }

    const hasCameraMetadata = (file) => {
      return file.scanner_manufacturer ||
             file.scanner_model_name ||
             file.scanning_software_name ||
             file.scanning_software_version
    }

    const getCategoryLabel = (category) => {
      const labels = {
        master: 'Master (Conservazione)',
        normalized: 'Normalizzato',
        export_high: 'Export Alta Qualità',
        export_low: 'Export Bassa Qualità',
        metadata: 'Metadati',
        icc: 'Profili Colore',
        logs: 'Log',
        other: 'Altro'
      }
      return labels[category] || category
    }

    const getCategoryIcon = (category) => {
      const icons = {
        master: '🎞️',
        normalized: '📸',
        export_high: '🖼️',
        export_low: '🏞️',
        metadata: '📄',
        icc: '🎨',
        logs: '📝',
        other: '📦'
      }
      return icons[category] || '📁'
    }

    // Watchers
    watch(() => activeTab.value, (newTab) => {
      if (newTab === 'files') {
        nextTick(() => {
          loadAllImagePreviews()
        })
      }
    })

    return {
      isEditing,
      saving,
      deleting,
      selectedFile,
      deletingFileId,
      imageDataUrl,
      showImageViewer,
      showFileDetail,
      imageUploading,
      imageUploadProgress,
      activeTab,
      editForm,
      imageFiles,
      filesByCategory,
      hasArchiveInfo,
      loadingFiles,
      loadingThumbnails,
      closeModal,
      closeFileDetail,
      startEdit,
      cancelEdit,
      saveChanges,
      deleteDocument,
      selectFile,
      downloadFile,
      deleteFile,
      validateAndSetImage,
      handleImageDrop,
      getFileThumbnail,
      formatDate,
      formatFileSize,
      isImageFile,
      isDNGFile,
      hasMetadata,
      hasCameraMetadata,
      getCategoryLabel,
      getCategoryIcon
    }
  }
}
</script>

<style scoped>
.file-category {
  margin-bottom: 24px;
}

:deep(.ant-tabs-tab) {
  font-weight: 500;
}

:deep(.ant-collapse-header) {
  font-weight: 500;
}
</style>
