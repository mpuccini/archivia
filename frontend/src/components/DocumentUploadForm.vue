<template>
  <div class="max-w-4xl mx-auto">
    <!-- Version Badge -->
    <div class="mb-4 flex justify-center">
      <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
        ✨ NEW WIZARD v2.0 ✨
      </span>
    </div>
    
    <!-- Wizard Header -->
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Upload New Document</h2>
      <p class="text-gray-600">Follow the steps to upload and catalog your document</p>
    </div>

    <!-- Progress Steps -->
    <div class="mb-8">
      <nav class="flex justify-center" aria-label="Progress">
        <ol class="flex items-start">
          <li 
            v-for="(step, index) in steps" 
            :key="step.id"
            class="relative flex flex-col items-center"
            :class="index < steps.length - 1 ? 'mr-8' : ''"
          >
            <!-- Step Circle -->
            <div 
              :class="[
                'flex h-12 w-12 items-center justify-center rounded-full border-2 text-sm font-semibold transition-all duration-200 relative z-10',
                index < currentStep 
                  ? 'border-blue-600 bg-blue-600 text-white shadow-md' 
                  : index === currentStep
                  ? 'border-blue-600 bg-white text-blue-600 shadow-md ring-2 ring-blue-200'
                  : 'border-gray-300 bg-white text-gray-400'
              ]"
            >
              <svg 
                v-if="index < currentStep" 
                class="h-6 w-6" 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span v-else class="text-sm font-bold">{{ index + 1 }}</span>
            </div>
            
            <!-- Connector Line - positioned between circles -->
            <div 
              v-if="index < steps.length - 1" 
              :class="[
                'absolute top-6 left-12 h-0.5 w-8 transition-colors duration-200 z-0',
                index < currentStep ? 'bg-blue-600' : 'bg-gray-300'
              ]"
            />
            
            <!-- Step Label -->
            <div class="text-center mt-3 max-w-20">
              <span 
                :class="[
                  'text-xs font-medium block leading-tight',
                  index <= currentStep ? 'text-gray-900' : 'text-gray-500'
                ]"
              >
                {{ step.name }}
              </span>
              <span 
                v-if="index === currentStep"
                class="text-xs text-blue-600 font-medium mt-1 block"
              >
                Active
              </span>
            </div>
          </li>
        </ol>
      </nav>
    </div>

    <!-- Wizard Content -->
    <div class="bg-white shadow-sm rounded-lg border border-gray-200">
      <!-- Step 1: File Upload -->
      <div v-if="currentStep === 0" class="p-8">
        <div class="text-center">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Upload Your Document</h3>
          <p class="text-gray-600 mb-8">Select image files to begin the cataloging process</p>
        </div>

        <!-- File Drop Zone -->
        <div 
          @drop="handleDrop"
          @dragover.prevent
          @dragenter.prevent="isDragOver = true"
          @dragleave.prevent="isDragOver = false"
          @click="triggerFileInput"
          :class="[
            'relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            isDragOver 
              ? 'border-blue-400 bg-blue-50' 
              : selectedFiles.length 
              ? 'border-green-400 bg-green-50' 
              : 'border-gray-300 hover:border-gray-400'
          ]"
        >
          <input
            ref="fileInput"
            type="file"
            @change="handleFileSelect"
            accept="image/*,.pdf"
            class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            multiple
          />

          <div v-if="!selectedFiles.length">
            <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <p class="mt-4 text-lg text-gray-600">
              <span class="font-medium text-blue-600">Click to upload</span> or drag and drop
            </p>
            <p class="text-sm text-gray-500">PNG, JPG, TIFF, PDF up to 50MB each</p>
          </div>

          <div v-else class="space-y-4">
            <svg class="mx-auto h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p class="text-lg font-medium text-gray-900">{{ selectedFiles.length }} file(s) selected</p>
              <div class="mt-2 space-y-2">
                <div v-for="(file, index) in selectedFiles" :key="file.name" class="flex items-center justify-between bg-white rounded-lg border p-3">
                  <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                      <svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ file.name }}</p>
                      <p class="text-sm text-gray-500">{{ formatFileSize(file.size) }}</p>
                    </div>
                  </div>
                  <button
                    @click.stop="removeFile(index)"
                    class="text-red-500 hover:text-red-700"
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            <button
              @click.stop="clearFiles"
              class="text-sm text-gray-500 hover:text-gray-700"
            >
              Clear all files
            </button>
          </div>
        </div>

        <!-- Auto-extracted filename preview -->
        <div v-if="selectedFiles.length" class="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 class="text-sm font-medium text-blue-900 mb-2">Auto-extracted Document ID</h4>
          <p class="text-sm text-blue-700">{{ extractedLogicalId }}</p>
          <p class="text-xs text-blue-600 mt-1">This will be used as the default Logical ID (you can modify it in the next step)</p>
        </div>
      </div>

      <!-- Step 2: Basic Information -->
      <div v-if="currentStep === 1" class="p-8">
        <h3 class="text-lg font-medium text-gray-900 mb-6">Basic Information</h3>
        
        <div class="space-y-6">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="logical_id" class="block text-sm font-medium text-gray-700">Logical ID *</label>
              <input
                type="text"
                id="logical_id"
                v-model="formData.logical_id"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                :placeholder="extractedLogicalId"
                required
              />
              <p class="mt-1 text-sm text-gray-500">Unique identifier for this document</p>
            </div>

            <div>
              <label for="conservative_id" class="block text-sm font-medium text-gray-700">Conservative ID</label>
              <input
                type="text"
                id="conservative_id"
                v-model="formData.conservative_id"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., IT-MO0172"
              />
              <p class="mt-1 text-sm text-gray-500">Archive's internal reference number</p>
            </div>
          </div>

          <div>
            <label for="title" class="block text-sm font-medium text-gray-700">Title</label>
            <input
              type="text"
              id="title"
              v-model="formData.title"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Document title"
            />
          </div>

          <div>
            <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              id="description"
              v-model="formData.description"
              rows="3"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Brief description of the document content"
            />
          </div>

          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="document_type" class="block text-sm font-medium text-gray-700">Document Type</label>
              <select
                id="document_type"
                v-model="formData.document_type"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Select type</option>
                <option value="manuscript">Manuscript</option>
                <option value="photograph">Photograph</option>
                <option value="letter">Letter</option>
                <option value="document">Document</option>
                <option value="map">Map</option>
                <option value="drawing">Drawing</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label for="total_pages" class="block text-sm font-medium text-gray-700">Total Pages</label>
              <input
                type="number"
                id="total_pages"
                v-model.number="formData.total_pages"
                min="1"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Number of pages"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: Archive Information -->
      <div v-if="currentStep === 2" class="p-8">
        <h3 class="text-lg font-medium text-gray-900 mb-6">Archive Information</h3>
        
        <div class="space-y-6">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="archive_name" class="block text-sm font-medium text-gray-700">Archive Name</label>
              <input
                type="text"
                id="archive_name"
                v-model="formData.archive_name"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Archivio di Stato di Modena"
              />
            </div>

            <div>
              <label for="archive_contact" class="block text-sm font-medium text-gray-700">Archive Contact</label>
              <input
                type="email"
                id="archive_contact"
                v-model="formData.archive_contact"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., as-mo@cultura.gov.it"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
            <div>
              <label for="fund_name" class="block text-sm font-medium text-gray-700">Fund Name</label>
              <input
                type="text"
                id="fund_name"
                v-model="formData.fund_name"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Fondo Fotografico"
              />
            </div>

            <div>
              <label for="series_name" class="block text-sm font-medium text-gray-700">Series Name</label>
              <input
                type="text"
                id="series_name"
                v-model="formData.series_name"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Serie I"
              />
            </div>

            <div>
              <label for="folder_number" class="block text-sm font-medium text-gray-700">Folder/Unit Number</label>
              <input
                type="text"
                id="folder_number"
                v-model="formData.folder_number"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Busta 45"
              />
            </div>
          </div>

          <div>
            <label for="conservative_id_authority" class="block text-sm font-medium text-gray-700">ID Authority</label>
            <input
              type="text"
              id="conservative_id_authority"
              v-model="formData.conservative_id_authority"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., ISIL"
            />
            <p class="mt-1 text-sm text-gray-500">Authority that assigned the conservative ID</p>
          </div>
        </div>
      </div>

      <!-- Step 4: Dates and Context -->
      <div v-if="currentStep === 3" class="p-8">
        <h3 class="text-lg font-medium text-gray-900 mb-6">Dates and Context</h3>
        
        <div class="space-y-6">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="date_from" class="block text-sm font-medium text-gray-700">Date From</label>
              <input
                type="date"
                id="date_from"
                v-model="formData.date_from"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <div>
              <label for="date_to" class="block text-sm font-medium text-gray-700">Date To</label>
              <input
                type="date"
                id="date_to"
                v-model="formData.date_to"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="period" class="block text-sm font-medium text-gray-700">Historical Period</label>
              <input
                type="text"
                id="period"
                v-model="formData.period"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Renaissance, 20th Century"
              />
            </div>

            <div>
              <label for="location" class="block text-sm font-medium text-gray-700">Location</label>
              <input
                type="text"
                id="location"
                v-model="formData.location"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Modena, Italy"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label for="language" class="block text-sm font-medium text-gray-700">Language</label>
              <select
                id="language"
                v-model="formData.language"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Select language</option>
                <option value="it">Italian</option>
                <option value="en">English</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="es">Spanish</option>
                <option value="la">Latin</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label for="subjects" class="block text-sm font-medium text-gray-700">Subjects/Keywords</label>
              <input
                type="text"
                id="subjects"
                v-model="formData.subjects"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., architecture, portrait, landscape"
              />
              <p class="mt-1 text-sm text-gray-500">Separate multiple subjects with commas</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 5: Review and Submit -->
      <div v-if="currentStep === 4" class="p-8">
        <h3 class="text-lg font-medium text-gray-900 mb-6">Review and Submit</h3>
        
        <!-- Files Summary -->
        <div class="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 class="text-md font-medium text-gray-900 mb-3">Files to Upload</h4>
          <div class="space-y-2">
            <div v-for="file in selectedFiles" :key="file.name" class="flex items-center justify-between text-sm">
              <span class="text-gray-900">{{ file.name }}</span>
              <span class="text-gray-500">{{ formatFileSize(file.size) }}</span>
            </div>
          </div>
        </div>

        <!-- Form Data Summary -->
        <div class="space-y-6">
          <div class="border-b border-gray-200 pb-4">
            <h4 class="text-md font-medium text-gray-900 mb-3">Basic Information</h4>
            <dl class="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <div v-if="formData.logical_id">
                <dt class="text-sm font-medium text-gray-500">Logical ID</dt>
                <dd class="text-sm text-gray-900">{{ formData.logical_id }}</dd>
              </div>
              <div v-if="formData.conservative_id">
                <dt class="text-sm font-medium text-gray-500">Conservative ID</dt>
                <dd class="text-sm text-gray-900">{{ formData.conservative_id }}</dd>
              </div>
              <div v-if="formData.title">
                <dt class="text-sm font-medium text-gray-500">Title</dt>
                <dd class="text-sm text-gray-900">{{ formData.title }}</dd>
              </div>
              <div v-if="formData.document_type">
                <dt class="text-sm font-medium text-gray-500">Document Type</dt>
                <dd class="text-sm text-gray-900">{{ formData.document_type }}</dd>
              </div>
            </dl>
          </div>

          <div v-if="formData.archive_name || formData.fund_name || formData.series_name" class="border-b border-gray-200 pb-4">
            <h4 class="text-md font-medium text-gray-900 mb-3">Archive Information</h4>
            <dl class="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <div v-if="formData.archive_name">
                <dt class="text-sm font-medium text-gray-500">Archive Name</dt>
                <dd class="text-sm text-gray-900">{{ formData.archive_name }}</dd>
              </div>
              <div v-if="formData.fund_name">
                <dt class="text-sm font-medium text-gray-500">Fund Name</dt>
                <dd class="text-sm text-gray-900">{{ formData.fund_name }}</dd>
              </div>
              <div v-if="formData.series_name">
                <dt class="text-sm font-medium text-gray-500">Series Name</dt>
                <dd class="text-sm text-gray-900">{{ formData.series_name }}</dd>
              </div>
              <div v-if="formData.folder_number">
                <dt class="text-sm font-medium text-gray-500">Folder/Unit</dt>
                <dd class="text-sm text-gray-900">{{ formData.folder_number }}</dd>
              </div>
            </dl>
          </div>

          <div v-if="formData.date_from || formData.location || formData.language" class="pb-4">
            <h4 class="text-md font-medium text-gray-900 mb-3">Context Information</h4>
            <dl class="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <div v-if="formData.date_from">
                <dt class="text-sm font-medium text-gray-500">Date From</dt>
                <dd class="text-sm text-gray-900">{{ formData.date_from }}</dd>
              </div>
              <div v-if="formData.date_to">
                <dt class="text-sm font-medium text-gray-500">Date To</dt>
                <dd class="text-sm text-gray-900">{{ formData.date_to }}</dd>
              </div>
              <div v-if="formData.location">
                <dt class="text-sm font-medium text-gray-500">Location</dt>
                <dd class="text-sm text-gray-900">{{ formData.location }}</dd>
              </div>
              <div v-if="formData.language">
                <dt class="text-sm font-medium text-gray-500">Language</dt>
                <dd class="text-sm text-gray-900">{{ formData.language }}</dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- Upload Progress -->
        <div v-if="uploading" class="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 class="text-sm font-medium text-blue-900 mb-2">Upload Progress</h4>
          <div class="w-full bg-blue-200 rounded-full h-2">
            <div 
              class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
              :style="{ width: uploadProgress + '%' }"
            ></div>
          </div>
          <p class="mt-1 text-xs text-blue-700">{{ uploadStatus }}</p>
        </div>
      </div>

      <!-- Navigation Buttons -->
      <div class="border-t border-gray-200 px-8 py-4 flex justify-between">
        <button
          v-if="currentStep > 0"
          @click="previousStep"
          :disabled="uploading"
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Previous
        </button>
        <div v-else></div>

        <div class="flex space-x-3">
          <button
            @click="$emit('cancel')"
            :disabled="uploading"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>

          <button
            v-if="currentStep < steps.length - 1"
            @click="nextStep"
            :disabled="!canProceedToNextStep || uploading"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            v-else
            @click="submitForm"
            :disabled="!canSubmit || uploading"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="uploading" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ uploading ? 'Uploading...' : 'Upload Document' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-4 p-4 bg-red-50 rounded-lg border border-red-200">
      <div class="flex">
        <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Upload Error</h3>
          <p class="mt-1 text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

export default {
  name: 'DocumentUploadForm',
  emits: ['upload-complete', 'cancel'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    
    // State
    const currentStep = ref(0)
    const selectedFiles = ref([])
    const isDragOver = ref(false)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const error = ref('')
    const fileInput = ref(null)

    // Steps configuration
    const steps = [
      { id: 'upload', name: 'Upload Files' },
      { id: 'basic', name: 'Basic Info' },
      { id: 'archive', name: 'Archive Info' },
      { id: 'context', name: 'Dates & Context' },
      { id: 'review', name: 'Review & Submit' }
    ]

    // Form data
    const formData = reactive({
      logical_id: '',
      conservative_id: '',
      title: '',
      description: '',
      archive_name: '',
      archive_contact: '',
      fund_name: '',
      series_name: '',
      folder_number: '',
      conservative_id_authority: '',
      document_type: '',
      total_pages: null,
      date_from: '',
      date_to: '',
      period: '',
      location: '',
      language: '',
      subjects: ''
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
    const triggerFileInput = () => {
      fileInput.value?.click()
    }

    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      addFiles(files)
    }

    const handleDrop = (event) => {
      event.preventDefault()
      isDragOver.value = false
      const files = Array.from(event.dataTransfer.files)
      addFiles(files)
    }

    const addFiles = (files) => {
      // Filter for supported file types
      const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'application/pdf']
      const validFiles = files.filter(file => 
        supportedTypes.includes(file.type) && file.size <= 50 * 1024 * 1024 // 50MB limit
      )

      if (validFiles.length !== files.length) {
        error.value = 'Some files were skipped. Only JPEG, PNG, TIFF, and PDF files under 50MB are supported.'
      } else {
        error.value = ''
      }

      // Add valid files to selection
      selectedFiles.value.push(...validFiles)

      // Auto-fill logical ID if empty and this is the first file
      if (selectedFiles.value.length === validFiles.length && !formData.logical_id) {
        formData.logical_id = extractedLogicalId.value
      }
    }

    const removeFile = (index) => {
      selectedFiles.value.splice(index, 1)
      
      // Clear form if no files left
      if (selectedFiles.value.length === 0) {
        clearForm()
      }
    }

    const clearFiles = () => {
      selectedFiles.value = []
      clearForm()
    }

    const clearForm = () => {
      Object.keys(formData).forEach(key => {
        if (typeof formData[key] === 'string') {
          formData[key] = ''
        } else if (typeof formData[key] === 'number') {
          formData[key] = null
        }
      })
      if (fileInput.value) {
        fileInput.value.value = ''
      }
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

    const submitForm = async () => {
      if (!canSubmit.value) {
        error.value = 'Please complete all required fields and select at least one file.'
        return
      }

      uploading.value = true
      uploadProgress.value = 0
      uploadStatus.value = 'Preparing upload...'
      error.value = ''

      try {
        // Upload each file individually with the same metadata
        const uploadPromises = selectedFiles.value.map(async (file, index) => {
          const formDataToSend = new FormData()
          formDataToSend.append('file', file)
          
          // Add metadata for each file
          const fileSpecificData = {
            ...formData,
            logical_id: selectedFiles.value.length > 1 
              ? `${formData.logical_id}_${index + 1}` 
              : formData.logical_id,
            sequence_number: index + 1,
            total_files: selectedFiles.value.length
          }

          // Add all form fields
          for (const [key, value] of Object.entries(fileSpecificData)) {
            if (value !== null && value !== '') {
              formDataToSend.append(key, value)
            }
          }

          uploadStatus.value = `Uploading ${file.name}...`
          
          return axios.post(
            `${import.meta.env.VITE_API_URL}/api/documents/upload`,
            formDataToSend,
            {
              headers: {
                'Authorization': `Bearer ${authStore.token}`,
                'Content-Type': 'multipart/form-data'
              },
              onUploadProgress: (progressEvent) => {
                const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                const overallProgress = Math.round(((index * 100) + fileProgress) / selectedFiles.value.length)
                uploadProgress.value = overallProgress
                uploadStatus.value = `Uploading ${file.name}... ${fileProgress}%`
              }
            }
          )
        })

        const responses = await Promise.all(uploadPromises)
        
        uploadStatus.value = 'Upload complete!'
        uploadProgress.value = 100
        
        setTimeout(() => {
          emit('upload-complete', {
            documents: responses.map(r => r.data),
            count: responses.length
          })
        }, 1000)

      } catch (err) {
        console.error('Upload error:', err)
        error.value = err.response?.data?.detail || err.message || 'Upload failed'
        uploadStatus.value = 'Upload failed'
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
      // State
      currentStep,
      selectedFiles,
      isDragOver,
      uploading,
      uploadProgress,
      uploadStatus,
      error,
      fileInput,
      
      // Configuration
      steps,
      
      // Form data
      formData,
      
      // Computed
      extractedLogicalId,
      canProceedToNextStep,
      canSubmit,
      
      // Methods
      triggerFileInput,
      handleFileSelect,
      handleDrop,
      removeFile,
      clearFiles,
      formatFileSize,
      nextStep,
      previousStep,
      submitForm
    }
  }
}
</script>
