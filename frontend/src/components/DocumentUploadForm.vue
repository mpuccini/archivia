<template>
  <div class="document-upload-form">
    <!-- Intestazione -->
    <div class="form-header">
      <h1>Crea Nuovo Documento</h1>
      <p>Completa il modulo per catalogare il tuo documento archivistico</p>
    </div>

    <!-- Steps -->
    <a-steps :current="currentStep" class="steps-container">
      <a-step title="Caricamento e Info Base">
        <template #icon>
          <cloud-upload-outlined />
        </template>
      </a-step>
      <a-step title="Archivio e Contesto">
        <template #icon>
          <folder-open-outlined />
        </template>
      </a-step>
      <a-step title="Metadati ECO-MiC">
        <template #icon>
          <file-text-outlined />
        </template>
      </a-step>
      <a-step title="Revisione e Invio">
        <template #icon>
          <check-circle-outlined />
        </template>
      </a-step>
    </a-steps>

    <!-- Contenuto Steps -->
    <a-card class="step-content">
      <!-- Step 1: Caricamento File e Info Base -->
      <div v-if="currentStep === 0">
        <div class="step-header">
          <cloud-upload-outlined :style="{ fontSize: '32px', color: '#1890ff' }" />
          <h3>Carica i Tuoi File</h3>
          <p>Seleziona i file immagine per iniziare a catalogare il documento archivistico</p>
        </div>

        <!-- Sezione Importazione Metadati -->
        <a-card class="metadata-import-card" :bordered="false">
          <template #title>
            <file-text-outlined /> Opzionale: Importa Metadati
          </template>
          <p class="metadata-description">
            Carica un file CSV o XML per pre-compilare automaticamente i campi del modulo
          </p>

          <input
            ref="metadataFileInput"
            type="file"
            @change="handleMetadataFileSelect"
            accept=".csv,.xml,.mets"
            style="display: none"
          />

          <a-space direction="vertical" style="width: 100%">
            <a-button
              @click="triggerMetadataFileInput"
            >
              <template #icon>
                <inbox-outlined />
              </template>
              Scegli File Metadati
            </a-button>

            <div v-if="selectedMetadataFile" class="metadata-file-selected">
              <check-circle-outlined style="color: #52c41a" />
              <span>{{ selectedMetadataFile.name }}</span>
              <a-button
                type="text"
                danger
                size="small"
                @click="clearMetadataFile"
              >
                <template #icon>
                  <close-outlined />
                </template>
              </a-button>
            </div>

            <!-- Stato Elaborazione Metadati -->
            <a-alert
              v-if="metadataProcessing"
              message="Elaborazione file metadati in corso..."
              type="info"
              show-icon
            >
              <template #icon>
                <loading-outlined />
              </template>
            </a-alert>

            <!-- Successo Importazione -->
            <a-alert
              v-if="metadataImported"
              type="success"
              show-icon
            >
              <template #message>
                Metadati importati con successo!
              </template>
              <template #description>
                {{ importedFieldsCount }} campi sono stati pre-compilati nel modulo
              </template>
            </a-alert>

            <!-- Errore Importazione -->
            <a-alert
              v-if="metadataError"
              :message="metadataError"
              type="error"
              show-icon
              closable
              @close="metadataError = ''"
            />
          </a-space>
        </a-card>

        <!-- Area di Caricamento File -->
        <a-upload-dragger
          v-model:file-list="fileList"
          :before-upload="beforeUpload"
          :multiple="true"
          accept="image/*,.pdf,.dng"
          @change="handleFileChange"
          class="file-upload-dragger"
        >
          <p class="ant-upload-drag-icon">
            <inbox-outlined v-if="!selectedFiles.length" :style="{ fontSize: '48px', color: '#1890ff' }" />
            <check-circle-outlined v-else :style="{ fontSize: '48px', color: '#52c41a' }" />
          </p>
          <p class="ant-upload-text">
            <span v-if="!selectedFiles.length">Clicca o trascina i file in quest'area per caricarli</span>
            <span v-else>{{ selectedFiles.length }} file selezionato{{ selectedFiles.length > 1 ? 'i' : '' }}</span>
          </p>
          <p class="ant-upload-hint">
            Formati supportati: PNG, JPG, TIFF, DNG, PDF
            <br />
            (File DNG fino a 80GB, altri fino a 50MB)
          </p>
        </a-upload-dragger>

        <!-- ID Logico Estratto Automaticamente -->
        <a-alert
          v-if="selectedFiles.length"
          type="info"
          show-icon
          class="extracted-id-alert"
        >
          <template #message>
            ID Documento Estratto Automaticamente
          </template>
          <template #description>
            <strong>{{ extractedLogicalId }}</strong>
            <br />
            Questo sarà utilizzato come ID Logico predefinito
          </template>
        </a-alert>

        <a-divider>Informazioni Base</a-divider>

        <!-- Sezione Identificatori -->
        <a-card title="Identificatori Documento" :bordered="false" class="info-section">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item
                  label="ID Logico"
                  required
                  help="Identificatore univoco per questo documento"
                >
                  <a-input
                    v-model:value="formData.logical_id"
                    :placeholder="extractedLogicalId"
                    size="large"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item
                  label="ID Conservativo"
                  help="Riferimento interno dell'archivio"
                >
                  <a-input
                    v-model:value="formData.conservative_id"
                    placeholder="es. IT-MO0172"
                    size="large"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </a-card>

        <!-- Sezione Contenuto -->
        <a-card title="Descrizione Contenuto" :bordered="false" class="info-section">
          <a-form layout="vertical">
            <a-form-item label="Titolo">
              <a-input
                v-model:value="formData.title"
                placeholder="Inserisci il titolo del documento"
                size="large"
              />
            </a-form-item>
            <a-form-item label="Descrizione">
              <a-textarea
                v-model:value="formData.description"
                :rows="4"
                placeholder="Breve descrizione del contenuto e del significato del documento"
                size="large"
              />
            </a-form-item>
          </a-form>
        </a-card>

        <!-- Sezione Classificazione -->
        <a-card title="Classificazione" :bordered="false" class="info-section">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="Tipo di Documento">
                  <a-select
                    v-model:value="formData.document_type"
                    placeholder="Seleziona tipo"
                    size="large"
                  >
                    <a-select-option value="">Seleziona tipo</a-select-option>
                    <a-select-option value="manuscript">Manoscritto</a-select-option>
                    <a-select-option value="photograph">Fotografia</a-select-option>
                    <a-select-option value="letter">Lettera</a-select-option>
                    <a-select-option value="document">Documento</a-select-option>
                    <a-select-option value="map">Mappa</a-select-option>
                    <a-select-option value="drawing">Disegno</a-select-option>
                    <a-select-option value="other">Altro</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="Numero Totale Pagine">
                  <a-input-number
                    v-model:value="formData.total_pages"
                    :min="1"
                    placeholder="Numero di pagine"
                    size="large"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </a-card>
      </div>

      <!-- Step 2: Archivio e Contesto -->
      <div v-if="currentStep === 1">
        <div class="step-header">
          <folder-open-outlined :style="{ fontSize: '32px', color: '#1890ff' }" />
          <h3>Archivio e Contesto</h3>
          <p>Contesto archivistico, informazioni temporali e geografiche</p>
        </div>

        <!-- Dettagli Archivio -->
        <a-card title="Dettagli Archivio" :bordered="false" class="info-section">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="Nome Archivio">
                  <a-input
                    v-model:value="formData.archive_name"
                    placeholder="es. Archivio di Stato di Modena"
                    size="large"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="Contatto Archivio">
                  <a-input
                    v-model:value="formData.archive_contact"
                    type="email"
                    placeholder="es. as-mo@cultura.gov.it"
                    size="large"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </a-card>

        <!-- Gerarchia Archivistica -->
        <a-card title="Gerarchia Archivistica" :bordered="false" class="info-section">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="8">
                <a-form-item label="Nome Fondo">
                  <a-input
                    v-model:value="formData.fund_name"
                    placeholder="es. Fondo Fotografico"
                    size="large"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="Nome Serie">
                  <a-input
                    v-model:value="formData.series_name"
                    placeholder="es. Serie I"
                    size="large"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="Numero Fascicolo/Unità">
                  <a-input
                    v-model:value="formData.folder_number"
                    placeholder="es. Busta 45"
                    size="large"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </a-card>

        <!-- Autorità -->
        <a-card title="Autorità di Identificazione" :bordered="false" class="info-section">
          <a-form layout="vertical">
            <a-form-item
              label="Autorità ID"
              help="Autorità che ha assegnato l'ID conservativo"
            >
              <a-input
                v-model:value="formData.conservative_id_authority"
                placeholder="es. ISIL"
                size="large"
              />
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- Step 3: Metadati ECO-MiC -->
      <div v-if="currentStep === 2">
        <div class="step-header">
          <file-text-outlined :style="{ fontSize: '32px', color: '#722ed1' }" />
          <h3>Metadati ECO-MiC</h3>
          <p>Campi opzionali per la conformità METS ECO-MiC 1.1</p>
        </div>

        <!-- Tipo di Risorsa -->
        <a-card title="Tipo di Risorsa e Descrizione Fisica" :bordered="false" class="info-section ecomic-section">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item
                  label="Tipo di Risorsa"
                  help="Tipo di risorsa principale secondo lo standard ECO-MiC"
                >
                  <a-select
                    v-model:value="formData.type_of_resource"
                    placeholder="Seleziona tipo"
                    size="large"
                  >
                    <a-select-option value="">Seleziona tipo</a-select-option>
                    <a-select-option value="risorsa manoscritta">Risorsa manoscritta</a-select-option>
                    <a-select-option value="documento testuale">Documento testuale</a-select-option>
                    <a-select-option value="documento cartografico">Documento cartografico</a-select-option>
                    <a-select-option value="documento fotografico">Documento fotografico</a-select-option>
                    <a-select-option value="documento grafico">Documento grafico</a-select-option>
                    <a-select-option value="risorsa a stampa">Risorsa a stampa</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item
                  label="Forma Fisica"
                  help="Formato fisico con authority='gmd'"
                >
                  <a-input
                    v-model:value="formData.physical_form"
                    placeholder="es. documento testuale, mappa"
                    size="large"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-form-item
              label="Descrizione Estensione"
              help="Estensione fisica dettagliata"
            >
              <a-input
                v-model:value="formData.extent_description"
                placeholder="es. c. 14 nel fascicolo, 1 volume, 25 carte"
                size="large"
              />
            </a-form-item>
          </a-form>
        </a-card>

        <!-- Produttore/Creatore -->
        <a-card title="Informazioni Produttore e Creatore" :bordered="false" class="info-section">
          <a-collapse :bordered="false" default-active-key="producer">
            <!-- Produttore -->
            <a-collapse-panel key="producer" header="Produttore (Autore/Compilatore)">
              <a-form layout="vertical">
                <a-form-item label="Nome Produttore">
                  <a-input
                    v-model:value="formData.producer_name"
                    placeholder="es. Monastero di San Colombano"
                    size="large"
                  />
                </a-form-item>
                <a-row :gutter="16">
                  <a-col :span="12">
                    <a-form-item label="Tipo Produttore">
                      <a-select
                        v-model:value="formData.producer_type"
                        size="large"
                      >
                        <a-select-option value="corporate">Ente</a-select-option>
                        <a-select-option value="personal">Persona</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>
                  <a-col :span="12">
                    <a-form-item label="Ruolo Produttore">
                      <a-input
                        v-model:value="formData.producer_role"
                        placeholder="es. producer, author, compiler"
                        size="large"
                      />
                    </a-form-item>
                  </a-col>
                </a-row>
              </a-form>
            </a-collapse-panel>

            <!-- Creatore -->
            <a-collapse-panel key="creator" header="Creatore (Contributore)">
              <a-form layout="vertical">
                <a-form-item label="Nome Creatore">
                  <a-input
                    v-model:value="formData.creator_name"
                    placeholder="es. Giovanni Rossi"
                    size="large"
                  />
                </a-form-item>
                <a-row :gutter="16">
                  <a-col :span="12">
                    <a-form-item label="Tipo Creatore">
                      <a-select
                        v-model:value="formData.creator_type"
                        size="large"
                      >
                        <a-select-option value="personal">Persona</a-select-option>
                        <a-select-option value="corporate">Ente</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>
                  <a-col :span="12">
                    <a-form-item label="Ruolo Creatore">
                      <a-input
                        v-model:value="formData.creator_role"
                        placeholder="es. creator, contributor, editor"
                        size="large"
                      />
                    </a-form-item>
                  </a-col>
                </a-row>
              </a-form>
            </a-collapse-panel>
          </a-collapse>
        </a-card>

        <!-- Metadati Diritti -->
        <a-card title="Metadati Diritti (metsrights)" :bordered="false" class="info-section rights-section">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item
                  label="Categoria Diritti"
                  help="Stato del copyright"
                >
                  <a-select
                    v-model:value="formData.rights_category"
                    placeholder="Seleziona categoria"
                    size="large"
                  >
                    <a-select-option value="">Seleziona categoria</a-select-option>
                    <a-select-option value="COPYRIGHTED">PROTETTO DA COPYRIGHT</a-select-option>
                    <a-select-option value="PUBLIC DOMAIN">PUBBLICO DOMINIO</a-select-option>
                    <a-select-option value="CONTRACTUAL">CONTRATTUALE</a-select-option>
                    <a-select-option value="OTHER">ALTRO</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item
                  label="Titolare Diritti"
                  help="Organizzazione/persona detentrice dei diritti"
                >
                  <a-input
                    v-model:value="formData.rights_holder"
                    placeholder="es. Archivio di Stato di Modena"
                    size="large"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item
                  label="Vincolo Diritti"
                  help="Codice dichiarazione diritti"
                >
                  <a-input
                    v-model:value="formData.rights_constraint"
                    placeholder="es. NoC-OKLR, InC, InC-EDU"
                    size="large"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item
                  label="URL Licenza"
                  help="Link ai dettagli della licenza"
                >
                  <a-input
                    v-model:value="formData.license_url"
                    type="url"
                    placeholder="https://creativecommons.org/..."
                    size="large"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-form-item label="Dichiarazione Diritti">
              <a-textarea
                v-model:value="formData.rights_statement"
                :rows="2"
                placeholder="Informazioni aggiuntive sui diritti"
                size="large"
              />
            </a-form-item>
          </a-form>
        </a-card>

        <!-- Metadati Tecnici -->
        <a-card title="Metadati Tecnici (Scanner/Immagine)" :bordered="false" class="info-section">
          <a-form layout="vertical">
            <a-row :gutter="16">
              <a-col :span="8">
                <a-form-item label="Produttore Immagine">
                  <a-input
                    v-model:value="formData.image_producer"
                    placeholder="es. EDS Gamma"
                    size="large"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="Produttore Scanner">
                  <a-input
                    v-model:value="formData.scanner_manufacturer"
                    placeholder="es. Metis Systems srl"
                    size="large"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="Modello Scanner">
                  <a-input
                    v-model:value="formData.scanner_model"
                    placeholder="es. DRS Scanner Model X"
                    size="large"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </a-card>

        <!-- Stato Record -->
        <a-card title="Stato Record" :bordered="false" class="info-section">
          <a-form layout="vertical">
            <a-form-item
              label="Stato Record"
              help="Livello di completamento METS (predefinito: COMPLETE)"
            >
              <a-select
                v-model:value="formData.record_status"
                size="large"
              >
                <a-select-option value="COMPLETE">COMPLETO</a-select-option>
                <a-select-option value="MINIMUM">MINIMO</a-select-option>
                <a-select-option value="REFERENCED">REFERENZIATO</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- Step 4: Revisione e Invio -->
      <div v-if="currentStep === 3">
        <div class="step-header">
          <check-circle-outlined :style="{ fontSize: '32px', color: '#52c41a' }" />
          <h3>Revisione e Invio</h3>
          <p>Verifica le informazioni prima di completare il caricamento</p>
        </div>

        <!-- Riepilogo File -->
        <a-card title="File da Caricare" :bordered="false" class="info-section">
          <a-list
            size="small"
            :data-source="selectedFiles"
            :render-item="(file) => ({
              key: file.name,
              content: h('div', { style: 'display: flex; justify-content: space-between; align-items: center;' }, [
                h('span', file.name),
                h('span', { style: 'color: #999;' }, formatFileSize(file.size))
              ])
            })"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
                  <span><file-outlined /> {{ item.name }}</span>
                  <span style="color: #999;">{{ formatFileSize(item.size) }}</span>
                </div>
              </a-list-item>
            </template>
          </a-list>
        </a-card>


        <!-- Riepilogo Dati Modulo -->
        <a-card title="Informazioni Base" :bordered="false" class="info-section" v-if="formData.logical_id || formData.conservative_id || formData.title || formData.document_type">
          <a-descriptions :column="2" bordered size="small">
            <a-descriptions-item label="ID Logico" v-if="formData.logical_id">
              {{ formData.logical_id }}
            </a-descriptions-item>
            <a-descriptions-item label="ID Conservativo" v-if="formData.conservative_id">
              {{ formData.conservative_id }}
            </a-descriptions-item>
            <a-descriptions-item label="Titolo" v-if="formData.title" :span="2">
              {{ formData.title }}
            </a-descriptions-item>
            <a-descriptions-item label="Tipo Documento" v-if="formData.document_type">
              {{ formData.document_type }}
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="Informazioni Archivio" :bordered="false" class="info-section" v-if="formData.archive_name || formData.fund_name || formData.series_name || formData.folder_number">
          <a-descriptions :column="2" bordered size="small">
            <a-descriptions-item label="Nome Archivio" v-if="formData.archive_name" :span="2">
              {{ formData.archive_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Nome Fondo" v-if="formData.fund_name">
              {{ formData.fund_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Nome Serie" v-if="formData.series_name">
              {{ formData.series_name }}
            </a-descriptions-item>
            <a-descriptions-item label="Fascicolo/Unità" v-if="formData.folder_number">
              {{ formData.folder_number }}
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </div>
    </a-card>

    <!-- Fullscreen Upload Progress -->
    <div v-if="uploading" class="upload-overlay">
      <a-spin size="large" :spinning="true">
        <template #indicator>
          <loading-outlined style="font-size: 48px" spin />
        </template>
        <div class="upload-progress-container">
          <h3>Caricamento in corso...</h3>
          <a-progress
            :percent="uploadProgress"
            :status="uploadProgress === 100 ? 'success' : 'active'"
            :stroke-width="12"
          />
          <p class="upload-status-text">{{ uploadStatus }}</p>
          <p class="upload-percentage">{{ uploadProgress }}%</p>
        </div>
      </a-spin>
    </div>

    <!-- Success Result -->
    <a-result
      v-if="uploadSuccess"
      status="success"
      title="Documento creato con successo"
      sub-title="Il documento è stato caricato e catalogato correttamente nel sistema"
    >
      <template #extra>
        <a-space>
          <a-button type="primary" @click="createAnother">
            Crea Altro Documento
          </a-button>
          <a-button @click="closeForm">
            Chiudi
          </a-button>
        </a-space>
      </template>
    </a-result>

    <!-- Pulsanti di Navigazione -->
    <div v-if="!uploadSuccess" class="navigation-buttons">
      <a-button
        v-if="currentStep > 0"
        size="large"
        @click="previousStep"
        :disabled="uploading"
      >
        <template #icon>
          <left-outlined />
        </template>
        Indietro
      </a-button>
      <div v-else></div>

      <a-space>
        <a-button
          size="large"
          @click="$emit('cancel')"
          :disabled="uploading"
        >
          Annulla
        </a-button>

        <a-button
          v-if="currentStep < 3"
          type="primary"
          size="large"
          @click="nextStep"
          :disabled="!canProceedToNextStep || uploading"
        >
          Avanti
          <template #icon>
            <right-outlined />
          </template>
        </a-button>

        <a-button
          v-else
          type="primary"
          size="large"
          @click="submitForm"
          :disabled="!canSubmit || uploading"
          :loading="uploading"
        >
          <template #icon v-if="!uploading">
            <upload-outlined />
          </template>
          {{ uploading ? 'Caricamento...' : 'Invia' }}
        </a-button>
      </a-space>
    </div>

    <!-- Messaggio di Errore -->
    <a-alert
      v-if="error"
      :message="error"
      type="error"
      show-icon
      closable
      @close="error = ''"
      style="margin-top: 16px"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, watch, h } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import { message } from 'ant-design-vue'
import {
  CloudUploadOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  CloseOutlined,
  LoadingOutlined,
  InboxOutlined,
  FolderOpenOutlined,
  LeftOutlined,
  RightOutlined,
  UploadOutlined,
  FileOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'DocumentUploadForm',
  components: {
    CloudUploadOutlined,
    FileTextOutlined,
    CheckCircleOutlined,
    CloseOutlined,
    LoadingOutlined,
    InboxOutlined,
    FolderOpenOutlined,
    LeftOutlined,
    RightOutlined,
    UploadOutlined,
    FileOutlined
  },
  emits: ['upload-complete', 'cancel'],
  setup(props, { emit }) {
    const authStore = useAuthStore()

    // State
    const currentStep = ref(0)
    const selectedFiles = ref([])
    const fileList = ref([])
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const error = ref('')
    const uploadSuccess = ref(false)

    // Metadata import state
    const selectedMetadataFile = ref(null)
    const metadataFileInput = ref(null)
    const metadataProcessing = ref(false)
    const metadataImported = ref(false)
    const metadataError = ref('')
    const importedFieldsCount = ref(0)

    // Steps configuration
    const steps = [
      { id: 'upload-basic', name: 'Caricamento e Info Base' },
      { id: 'archive-context', name: 'Archivio e Contesto' },
      { id: 'ecomic', name: 'Metadati ECO-MiC' },
      { id: 'review', name: 'Revisione e Invio' }
    ]

    // Form data
    const formData = reactive({
      logical_id: '',
      conservative_id: '',
      conservative_id_authority: '',
      title: '',
      description: '',
      archive_name: '',
      archive_contact: '',
      fund_name: '',
      series_name: '',
      folder_number: '',
      document_type: '',
      total_pages: null,
      date_from: '',
      date_to: '',
      period: '',
      location: '',
      language: '',
      subjects: '',
      // ECO-MiC specific fields
      type_of_resource: '',
      producer_name: '',
      producer_type: 'corporate',
      producer_role: '',
      creator_name: '',
      creator_type: 'personal',
      creator_role: '',
      rights_category: '',
      rights_holder: '',
      rights_constraint: '',
      license_url: '',
      rights_statement: '',
      physical_form: '',
      extent_description: '',
      image_producer: '',
      scanner_manufacturer: '',
      scanner_model: '',
      record_status: 'COMPLETE'
    })

    // Computed properties
    const extractedLogicalId = computed(() => {
      if (selectedFiles.value.length > 0) {
        const fileName = selectedFiles.value[0].name
        return fileName.replace(/\.[^/.]+$/, "")
      }
      return ''
    })

    const canProceedToNextStep = computed(() => {
      switch (currentStep.value) {
        case 0: // File upload step
          return selectedFiles.value.length > 0
        case 1: // Basic info step
          return formData.logical_id.trim() !== ''
        case 2: // Archive info step
        case 3: // Context step
          return true // These steps are optional
        default:
          return true
      }
    })

    const canSubmit = computed(() => {
      return selectedFiles.value.length > 0 &&
             formData.logical_id.trim() !== '' &&
             !uploading.value
    })

    // Methods
    const beforeUpload = (file) => {
      const supportedTypes = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/tiff',
        'image/x-adobe-dng',
        'image/dng',
        'application/pdf'
      ]

      const isDNG = file.type === 'image/x-adobe-dng' || file.type === 'image/dng' || file.name.toLowerCase().endsWith('.dng')
      const maxSize = isDNG ? 80 * 1024 * 1024 * 1024 : 50 * 1024 * 1024

      if (!supportedTypes.includes(file.type) && !isDNG) {
        message.error('Solo file JPEG, PNG, TIFF, DNG e PDF sono supportati')
        return false
      }

      if (file.size > maxSize) {
        message.error(`File troppo grande. Dimensione massima: ${isDNG ? '80GB' : '50MB'}`)
        return false
      }

      selectedFiles.value.push(file)

      // Auto-fill logical ID if empty and this is the first file
      if (selectedFiles.value.length === 1 && !formData.logical_id) {
        formData.logical_id = extractedLogicalId.value
      }

      return false // Prevent auto upload
    }

    const handleFileChange = ({ fileList: newFileList }) => {
      fileList.value = newFileList
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const nextStep = () => {
      if (canProceedToNextStep.value && currentStep.value < steps.length - 1) {
        currentStep.value++
      }
    }

    const previousStep = () => {
      if (currentStep.value > 0) {
        currentStep.value--
      }
    }

    // Metadata import methods
    const triggerMetadataFileInput = () => {
      metadataFileInput.value?.click()
    }

    const handleMetadataFileSelect = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      selectedMetadataFile.value = file
      metadataError.value = ''
      metadataImported.value = false
      importedFieldsCount.value = 0

      try {
        await processMetadataFile(file)
      } catch (err) {
        console.error('Metadata processing error:', err)
        metadataError.value = err.message || 'Impossibile elaborare il file metadati'
      }
    }

    const processMetadataFile = async (file) => {
      metadataProcessing.value = true

      try {
        const fileContent = await readFileContent(file)
        let parsedData = {}

        if (file.name.toLowerCase().endsWith('.csv')) {
          parsedData = parseCSVMetadata(fileContent)
        } else if (file.name.toLowerCase().endsWith('.xml') || file.name.toLowerCase().endsWith('.mets')) {
          parsedData = parseXMLMetadata(fileContent)
        } else {
          throw new Error('Formato file non supportato. Utilizzare file CSV o XML.')
        }

        // Apply parsed data to form
        applyMetadataToForm(parsedData)

        metadataImported.value = true
        metadataProcessing.value = false
        message.success('Metadati importati con successo!')
      } catch (err) {
        metadataProcessing.value = false
        throw err
      }
    }

    const readFileContent = (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target.result)
        reader.onerror = () => reject(new Error('Impossibile leggere il file'))
        reader.readAsText(file)
      })
    }

    const parseCSVMetadata = (csvContent) => {
      const lines = csvContent.trim().split('\n')
      if (lines.length < 2) {
        throw new Error('Il file CSV deve avere almeno una riga di intestazione e una riga di dati')
      }

      const headers = lines[0].split(',').map(h => h.trim().replace(/['"]/g, ''))
      const values = lines[1].split(',').map(v => v.trim().replace(/['"]/g, ''))

      const data = {}
      headers.forEach((header, index) => {
        if (values[index] && values[index] !== '') {
          const fieldName = mapHeaderToField(header)
          if (fieldName) {
            data[fieldName] = values[index]
          }
        }
      })

      return data
    }

    const parseXMLMetadata = (xmlContent) => {
      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(xmlContent, 'text/xml')

      if (xmlDoc.getElementsByTagName('parsererror').length > 0) {
        throw new Error('Formato XML non valido')
      }

      const data = {}

      // Helper function to get text content from elements
      const getElementText = (tagName, attribute = null, attributeValue = null) => {
        let elements = xmlDoc.getElementsByTagName(tagName)

        if (elements.length === 0) {
          const localName = tagName.includes(':') ? tagName.split(':')[1] : tagName
          elements = xmlDoc.getElementsByTagName(localName)
        }

        if (elements.length === 0) {
          const allElements = xmlDoc.getElementsByTagName('*')
          const matchingElements = []
          for (let element of allElements) {
            const localName = tagName.includes(':') ? tagName.split(':')[1] : tagName
            if (element.localName === localName || element.tagName.endsWith(':' + localName)) {
              matchingElements.push(element)
            }
          }
          elements = matchingElements
        }

        for (let element of elements) {
          if (attribute && attributeValue) {
            if (element.getAttribute(attribute) === attributeValue) {
              const text = element.textContent.trim()
              if (text) return text
            }
          } else if (!attribute) {
            const text = element.textContent.trim()
            if (text) return text
          }
        }
        return null
      }

      // Field mappings (simplified version)
      const fieldMappings = [
        { getter: () => getElementText('mods:identifier', 'type', 'logical'), field: 'logical_id' },
        { getter: () => getElementText('identifier', 'type', 'logical'), field: 'logical_id' },
        { getter: () => getElementText('mods:identifier', 'type', 'conservative'), field: 'conservative_id' },
        { getter: () => getElementText('identifier', 'type', 'conservative'), field: 'conservative_id' },
        { getter: () => getElementText('mods:title'), field: 'title' },
        { getter: () => getElementText('title'), field: 'title' },
        { getter: () => getElementText('mods:abstract'), field: 'description' },
        { getter: () => getElementText('abstract'), field: 'description' },
      ]

      fieldMappings.forEach(({ getter, field }) => {
        try {
          const value = getter()
          if (value && value !== '' && !data[field]) {
            data[field] = value
          }
        } catch (e) {
          console.warn(`Errore nell'elaborazione del campo ${field}:`, e)
        }
      })

      return data
    }

    const mapHeaderToField = (header) => {
      const normalizedHeader = header.toLowerCase().replace(/[^a-z0-9]/g, '_')

      const headerMappings = {
        'logical_id': 'logical_id',
        'logicalid': 'logical_id',
        'id': 'logical_id',
        'identifier': 'logical_id',
        'conservative_id': 'conservative_id',
        'conservativeid': 'conservative_id',
        'title': 'title',
        'description': 'description',
        'archive_name': 'archive_name',
        'archivename': 'archive_name',
      }

      return headerMappings[normalizedHeader] || null
    }

    const applyMetadataToForm = (parsedData) => {
      let fieldsCount = 0

      Object.keys(parsedData).forEach(field => {
        if (formData.hasOwnProperty(field) && parsedData[field]) {
          formData[field] = parsedData[field]
          fieldsCount++
        }
      })

      importedFieldsCount.value = fieldsCount

      if (fieldsCount === 0) {
        throw new Error('Nessun campo corrispondente trovato nel file metadati. Controllare i nomi dei campi.')
      }
    }

    const clearMetadataFile = () => {
      selectedMetadataFile.value = null
      metadataImported.value = false
      metadataError.value = ''
      importedFieldsCount.value = 0
      if (metadataFileInput.value) {
        metadataFileInput.value.value = ''
      }
    }

    const createAnother = () => {
      // Reset form
      uploadSuccess.value = false
      currentStep.value = 0
      selectedFiles.value = []
      fileList.value = []
      uploadProgress.value = 0
      uploadStatus.value = ''
      error.value = ''

      // Reset form data
      Object.keys(formData).forEach(key => {
        if (key === 'producer_type') {
          formData[key] = 'corporate'
        } else if (key === 'creator_type') {
          formData[key] = 'personal'
        } else if (key === 'record_status') {
          formData[key] = 'COMPLETE'
        } else if (key === 'total_pages') {
          formData[key] = null
        } else {
          formData[key] = ''
        }
      })

      clearMetadataFile()
    }

    const closeForm = () => {
      emit('cancel')
    }

    const submitForm = async () => {
      if (!canSubmit.value) {
        error.value = 'Completare tutti i campi obbligatori e selezionare almeno un file.'
        message.error('Completare tutti i campi obbligatori')
        return
      }

      uploading.value = true
      uploadProgress.value = 0
      uploadStatus.value = 'Preparazione caricamento...'
      error.value = ''

      try {
        // STEP 1: Create the document with metadata (using first file)
        uploadStatus.value = 'Creazione documento...'
        const firstFileFormData = new FormData()
        firstFileFormData.append('file', selectedFiles.value[0])

        // Add all metadata fields
        for (const [key, value] of Object.entries(formData)) {
          if (value !== null && value !== '') {
            firstFileFormData.append(key, value)
          }
        }

        const createResponse = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/documents/upload`,
          firstFileFormData,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              uploadProgress.value = Math.round(fileProgress / (selectedFiles.value.length + 1))
              uploadStatus.value = `Creazione documento... ${fileProgress}%`
            }
          }
        )

        const createdDocument = createResponse.data

        // STEP 2: Upload remaining files to the created document
        if (selectedFiles.value.length > 1) {
          const remainingFiles = selectedFiles.value.slice(1)

          for (let i = 0; i < remainingFiles.length; i++) {
            const file = remainingFiles[i]
            const fileFormData = new FormData()
            fileFormData.append('file', file)

            uploadStatus.value = `Caricamento ${file.name}... (${i + 2}/${selectedFiles.value.length})`

            await axios.post(
              `${import.meta.env.VITE_API_URL}/api/documents/${createdDocument.id}/images`,
              fileFormData,
              {
                headers: {
                  'Authorization': `Bearer ${authStore.token}`,
                  'Content-Type': 'multipart/form-data'
                },
                onUploadProgress: (progressEvent) => {
                  const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                  const overallProgress = Math.round(((i + 1) * 100 + fileProgress) / (selectedFiles.value.length + 1))
                  uploadProgress.value = overallProgress
                  uploadStatus.value = `Caricamento ${file.name}... ${fileProgress}%`
                }
              }
            )
          }
        }

        uploadStatus.value = 'Caricamento completato!'
        uploadProgress.value = 100
        message.success('Documento creato con successo!')

        // Show success result
        setTimeout(() => {
          uploading.value = false
          uploadSuccess.value = true
        }, 500)

        // Emit event after showing success
        setTimeout(() => {
          emit('upload-complete', {
            documents: [createdDocument],
            count: 1
          })
        }, 1000)

      } catch (err) {
        console.error('Upload error:', err)
        error.value = err.response?.data?.detail || err.message || 'Caricamento fallito'
        uploadStatus.value = 'Caricamento fallito'
        message.error('Errore durante il caricamento')
      } finally {
        uploading.value = false
      }
    }

    // Watch for auto-filled logical ID
    watch(extractedLogicalId, (newValue) => {
      if (newValue && !formData.logical_id) {
        formData.logical_id = newValue
      }
    })

    return {
      h,
      // State
      currentStep,
      selectedFiles,
      fileList,
      uploading,
      uploadProgress,
      uploadStatus,
      error,
      uploadSuccess,

      // Metadata import state
      selectedMetadataFile,
      metadataFileInput,
      metadataProcessing,
      metadataImported,
      metadataError,
      importedFieldsCount,

      // Configuration
      steps,

      // Form data
      formData,

      // Computed
      extractedLogicalId,
      canProceedToNextStep,
      canSubmit,

      // Methods
      beforeUpload,
      handleFileChange,
      formatFileSize,
      nextStep,
      previousStep,

      // Metadata import methods
      triggerMetadataFileInput,
      handleMetadataFileSelect,
      clearMetadataFile,

      // Success methods
      createAnother,
      closeForm,

      submitForm
    }
  }
}
</script>

<style scoped>
.document-upload-form {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-header h1 {
  font-size: 32px;
  font-weight: bold;
  color: #262626;
  margin-bottom: 8px;
}

.form-header p {
  font-size: 16px;
  color: #8c8c8c;
}

.steps-container {
  margin-bottom: 40px;
}

.step-content {
  margin-bottom: 24px;
  min-height: 500px;
}

.step-header {
  text-align: center;
  margin-bottom: 32px;
}

.step-header h3 {
  font-size: 24px;
  font-weight: bold;
  color: #262626;
  margin: 16px 0 8px 0;
}

.step-header p {
  font-size: 14px;
  color: #8c8c8c;
}

.metadata-import-card {
  background: linear-gradient(135deg, #e6f7ff 0%, #f0f5ff 100%);
  margin-bottom: 24px;
  border: 1px solid #91d5ff;
}

.metadata-description {
  color: #1890ff;
  margin-bottom: 16px;
}

.metadata-file-selected {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #d9d9d9;
}

.file-upload-dragger {
  margin-bottom: 24px;
}

.extracted-id-alert {
  margin-bottom: 24px;
}

.info-section {
  margin-bottom: 24px;
  background: #fafafa;
}

.ecomic-section {
  background: linear-gradient(135deg, #f9f0ff 0%, #f0f5ff 100%);
  border: 1px solid #d3adf7;
}

.rights-section {
  background: linear-gradient(135deg, #fff1f0 0%, #fff2e8 100%);
  border: 1px solid #ffbb96;
}

.validation-section {
  background: linear-gradient(135deg, #f6ffed 0%, #e6f7ff 100%);
  border: 1px solid #b7eb8f;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

:deep(.ant-upload-drag) {
  border-width: 2px;
  border-style: dashed;
  border-radius: 8px;
}

:deep(.ant-upload-drag:hover) {
  border-color: #40a9ff;
}

:deep(.ant-steps-item-title) {
  font-size: 14px !important;
}

:deep(.ant-card-head) {
  background: transparent;
  font-weight: 600;
}

:deep(.ant-form-item-label > label) {
  font-weight: 600;
}

.upload-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.upload-progress-container {
  background: white;
  padding: 48px;
  border-radius: 8px;
  min-width: 500px;
  text-align: center;
}

.upload-progress-container h3 {
  font-size: 24px;
  font-weight: bold;
  color: #262626;
  margin-bottom: 24px;
}

.upload-status-text {
  margin-top: 16px;
  font-size: 14px;
  color: #595959;
}

.upload-percentage {
  font-size: 32px;
  font-weight: bold;
  color: #1890ff;
  margin-top: 8px;
}
</style>
