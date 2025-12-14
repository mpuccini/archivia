<template>
  <div class="max-w-5xl mx-auto px-4 py-6">
    <!-- Wizard Header -->
    <div class="mb-10 text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Create New Document</h1>
      <p class="text-lg text-gray-600">Complete the form to catalog your archival document</p>
    </div>

    <!-- Progress Steps -->
    <div class="mb-10">
      <div class="flex items-center justify-between relative">
        <!-- Progress Bar Background -->
        <div class="absolute top-6 left-0 right-0 h-1 bg-gray-200 -z-10"></div>
        <!-- Active Progress Bar -->
        <div
          class="absolute top-6 left-0 h-1 bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500 -z-10"
          :style="{ width: `${(currentStep / (steps.length - 1)) * 100}%` }"
        ></div>

        <div
          v-for="(step, index) in steps"
          :key="step.id"
          class="flex flex-col items-center flex-1 relative"
        >
          <!-- Step Circle -->
          <div :class="[
            'w-14 h-14 rounded-full border-4 flex items-center justify-center font-bold relative z-10 transition-all duration-300 shadow-lg',
            index <= currentStep
              ? 'bg-gradient-to-br from-blue-500 to-blue-600 border-white text-white scale-110'
              : 'bg-white border-gray-300 text-gray-400'
          ]">
            <svg
              v-if="index < currentStep"
              class="w-7 h-7"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span v-else class="text-lg">{{ index + 1 }}</span>
          </div>

          <!-- Step Label -->
          <div :class="[
            'text-sm mt-3 text-center font-medium px-2',
            index === currentStep ? 'text-blue-600' : (index < currentStep ? 'text-gray-700' : 'text-gray-400')
          ]">
            {{ step.name }}
          </div>
        </div>
      </div>
    </div>

    <!-- Wizard Content -->
    <div class="bg-white shadow-xl rounded-2xl border border-gray-100 overflow-hidden">
      <!-- Step 1: File Upload -->
      <div v-if="currentStep === 0" class="p-8">
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Upload Your Files</h3>
          <p class="text-gray-600">Select image files to begin cataloging your archival document</p>
        </div>

        <!-- Metadata Import Section -->
        <div class="p-5 rounded-xl border-2 border-dashed border-blue-200 mb-8 bg-gradient-to-br from-blue-50 to-indigo-50">
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="flex-1">
              <h4 class="font-semibold text-blue-900 mb-2">Optional: Import Metadata</h4>
              <p class="text-sm text-blue-700 mb-4">Upload a CSV or XML file to pre-fill form fields automatically</p>
          
          <!-- Metadata file input -->
          <div class="flex items-center gap-4">
            <button
              @click="triggerMetadataFileInput"
              type="button"
            class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              Choose Metadata File
            </button>
            
            <div v-if="selectedMetadataFile" class="flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span class="font-medium text-green-700">{{ selectedMetadataFile.name }}</span>
              <button
                @click="clearMetadataFile"
                class="text-red-500 hover:text-red-700"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Hidden file input for metadata -->
          <input
            ref="metadataFileInput"
            type="file"
            @change="handleMetadataFileSelect"
            accept=".csv,.xml,.mets"
            class="hidden"
          />

          <!-- Metadata parsing status -->
          <div v-if="metadataProcessing" class="mt-4 p-3 bg-blue-100 rounded-lg">
            <div class="flex items-center">
              <svg class="animate-spin h-4 w-4 text-blue-600 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="text-sm text-blue-800">Processing metadata file...</span>
            </div>
          </div>

          <!-- Metadata import success -->
          <div v-if="metadataImported" class="mt-4 p-3 bg-green-100 rounded-lg">
            <div class="flex items-start">
              <svg class="h-4 w-4 text-green-500 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <div>
                <p class="text-sm font-medium text-green-800">Metadata imported successfully!</p>
                <p class="text-xs text-green-700 mt-1">{{ importedFieldsCount }} fields have been pre-filled in the form</p>
              </div>
            </div>
          </div>

          <!-- Metadata import error -->
          <div v-if="metadataError" class="mt-4 p-3 bg-red-100 rounded-lg">
            <div class="flex items-start">
              <svg class="h-4 w-4 text-red-500 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              <div>
                <p class="text-sm font-medium text-red-800">Error processing metadata file</p>
                <p class="text-xs text-red-700 mt-1">{{ metadataError }}</p>
              </div>
            </div>
          </div>
            </div>
          </div>
        </div>

        <!-- File Drop Zone -->
        <div
          @drop="handleDrop"
          @dragover.prevent
          @dragenter.prevent="isDragOver = true"
          @dragleave.prevent="isDragOver = false"
          @click="triggerFileInput"
          :class="[
            'border-3 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 transform',
            isDragOver ? 'border-blue-500 bg-blue-50 scale-102 shadow-lg' : 'border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-white hover:shadow-md',
            selectedFiles.length ? 'border-green-500 bg-green-50' : ''
          ]"
        >
          <input
            ref="fileInput"
            type="file"
            @change="handleFileSelect"
            accept="image/*,.pdf,.dng"
            class="hidden"
            multiple
          />

          <div v-if="!selectedFiles.length">
            <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full mb-4">
              <svg class="w-10 h-10 text-blue-600" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </div>
            <p class="mt-4 text-xl font-semibold text-gray-700">
              <span class="text-blue-600">Click to upload</span> or drag and drop
            </p>
            <p class="text-sm text-gray-500 mt-2">Supported: PNG, JPG, TIFF, DNG, PDF</p>
            <p class="text-xs text-gray-400 mt-1">(DNG files up to 80GB, others up to 50MB)</p>
          </div>

          <div v-else class="space-y-4">
            <div class="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
              <svg class="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p class="text-xl font-bold text-gray-900 mb-4">{{ selectedFiles.length }} file{{ selectedFiles.length > 1 ? 's' : '' }} selected</p>
              <div class="mt-4 space-y-2 max-h-48 overflow-y-auto">
                <div v-for="(file, index) in selectedFiles" :key="file.name" class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
                  <div class="flex items-center gap-3 flex-1">
                    <div class="flex-shrink-0 w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                      <svg class="h-6 w-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">{{ file.name }}</p>
                      <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
                    </div>
                  </div>
                  <button
                    @click.stop="removeFile(index)"
                    class="flex-shrink-0 w-8 h-8 flex items-center justify-center text-red-500 hover:bg-red-50 rounded-lg transition-colors"
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
              class="text-sm text-red-600 hover:text-red-700 font-medium mt-4 hover:underline"
            >
              Clear all files
            </button>
          </div>
        </div>

        <!-- Auto-extracted filename preview -->
        <div v-if="selectedFiles.length" class="mt-6 p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0">
              <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-blue-900 mb-1">Auto-extracted Document ID</h4>
              <p class="text-sm text-blue-700">{{ extractedLogicalId }}</p>
              <p class="text-xs text-blue-600 mt-1">This will be used as the default Logical ID below</p>
            </div>
          </div>
        </div>

        <!-- Basic Information Section (combined with Upload) -->
        <div class="space-y-6 mt-8">
          <!-- Identifiers Section -->
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border border-gray-200">
            <h4 class="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wide">Document Identifiers</h4>
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label for="logical_id" class="block text-sm font-semibold text-gray-700 mb-2">
                  Logical ID <span class="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="logical_id"
                  v-model="formData.logical_id"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  :placeholder="extractedLogicalId"
                  required
                />
                <p class="mt-2 text-xs text-gray-500">Unique identifier for this document</p>
              </div>

              <div>
                <label for="conservative_id" class="block text-sm font-semibold text-gray-700 mb-2">Conservative ID</label>
                <input
                  type="text"
                  id="conservative_id"
                  v-model="formData.conservative_id"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., IT-MO0172"
                />
                <p class="mt-2 text-xs text-gray-500">Archive's internal reference</p>
              </div>
            </div>
          </div>

          <!-- Content Section -->
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border border-gray-200">
            <h4 class="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wide">Content Description</h4>
            <div class="space-y-5">
              <div>
                <label for="title" class="block text-sm font-semibold text-gray-700 mb-2">Title</label>
                <input
                  type="text"
                  id="title"
                  v-model="formData.title"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="Enter document title"
                />
              </div>

              <div>
                <label for="description" class="block text-sm font-semibold text-gray-700 mb-2">Description</label>
                <textarea
                  id="description"
                  v-model="formData.description"
                  rows="4"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="Brief description of the document content and significance"
                />
              </div>
            </div>
          </div>

          <!-- Classification Section -->
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border border-gray-200">
            <h4 class="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wide">Classification</h4>
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label for="document_type" class="block text-sm font-semibold text-gray-700 mb-2">Document Type</label>
                <select
                  id="document_type"
                  v-model="formData.document_type"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
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
                <label for="total_pages" class="block text-sm font-semibold text-gray-700 mb-2">Total Pages</label>
                <input
                  type="number"
                  id="total_pages"
                  v-model.number="formData.total_pages"
                  min="1"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="Number of pages"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: Archive & Context -->
      <div v-if="currentStep === 1" class="p-8">
        <div class="mb-8">
          <div class="inline-flex items-center justify-center w-14 h-14 bg-blue-100 rounded-full mb-4">
            <svg class="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Archive & Context</h3>
          <p class="text-gray-600">Archival context, temporal and geographic information</p>
        </div>

        <div class="space-y-6">
          <!-- Archive Details Section -->
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border border-gray-200">
            <h4 class="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wide">Archive Details</h4>
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label for="archive_name" class="block text-sm font-semibold text-gray-700 mb-2">Archive Name</label>
                <input
                  type="text"
                  id="archive_name"
                  v-model="formData.archive_name"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., Archivio di Stato di Modena"
                />
              </div>

              <div>
                <label for="archive_contact" class="block text-sm font-semibold text-gray-700 mb-2">Archive Contact</label>
                <input
                  type="email"
                  id="archive_contact"
                  v-model="formData.archive_contact"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., as-mo@cultura.gov.it"
                />
              </div>
            </div>
          </div>

          <!-- Archival Hierarchy Section -->
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border border-gray-200">
            <h4 class="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wide">Archival Hierarchy</h4>
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
              <div>
                <label for="fund_name" class="block text-sm font-semibold text-gray-700 mb-2">Fund Name</label>
                <input
                  type="text"
                  id="fund_name"
                  v-model="formData.fund_name"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., Fondo Fotografico"
                />
              </div>

              <div>
                <label for="series_name" class="block text-sm font-semibold text-gray-700 mb-2">Series Name</label>
                <input
                  type="text"
                  id="series_name"
                  v-model="formData.series_name"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., Serie I"
                />
              </div>

              <div>
                <label for="folder_number" class="block text-sm font-semibold text-gray-700 mb-2">Folder/Unit Number</label>
                <input
                  type="text"
                  id="folder_number"
                  v-model="formData.folder_number"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., Busta 45"
                />
              </div>
            </div>
          </div>

          <!-- Authority Section -->
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border border-gray-200">
            <h4 class="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wide">Identification Authority</h4>
            <div>
              <label for="conservative_id_authority" class="block text-sm font-semibold text-gray-700 mb-2">ID Authority</label>
              <input
                type="text"
                id="conservative_id_authority"
                v-model="formData.conservative_id_authority"
                class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                placeholder="e.g., ISIL"
              />
              <p class="mt-2 text-xs text-gray-500">Authority that assigned the conservative ID</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: ECO-MiC Metadata -->
      <div v-if="currentStep === 2" class="p-8">
        <div class="mb-8">
          <div class="inline-flex items-center justify-center w-14 h-14 bg-purple-100 rounded-full mb-4">
            <svg class="w-7 h-7 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">ECO-MiC Metadata</h3>
          <p class="text-gray-600">Optional fields for METS ECO-MiC 1.2 compliance</p>
        </div>

        <div class="space-y-6">
          <!-- Type of Resource Section -->
          <div class="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200">
            <h4 class="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wide">Resource Type & Physical Description</h4>
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label for="type_of_resource" class="block text-sm font-semibold text-gray-700 mb-2">Type of Resource</label>
                <select
                  id="type_of_resource"
                  v-model="formData.type_of_resource"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                >
                  <option value="">Select type</option>
                  <option value="risorsa manoscritta">Risorsa manoscritta</option>
                  <option value="documento testuale">Documento testuale</option>
                  <option value="documento cartografico">Documento cartografico</option>
                  <option value="documento fotografico">Documento fotografico</option>
                  <option value="documento grafico">Documento grafico</option>
                  <option value="risorsa a stampa">Risorsa a stampa</option>
                </select>
                <p class="mt-2 text-xs text-gray-500">Main resource type per ECO-MiC standard</p>
              </div>

              <div>
                <label for="physical_form" class="block text-sm font-semibold text-gray-700 mb-2">Physical Form</label>
                <input
                  type="text"
                  id="physical_form"
                  v-model="formData.physical_form"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., documento testuale, mappa"
                />
                <p class="mt-2 text-xs text-gray-500">Physical format with authority="gmd"</p>
              </div>
            </div>

            <div class="mt-4">
              <label for="extent_description" class="block text-sm font-semibold text-gray-700 mb-2">Extent Description</label>
              <input
                type="text"
                id="extent_description"
                v-model="formData.extent_description"
                class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                placeholder="e.g., c. 14 nel fascicolo, 1 volume, 25 carte"
              />
              <p class="mt-2 text-xs text-gray-500">Detailed physical extent</p>
            </div>
          </div>

          <!-- Producer/Creator Section -->
          <div class="bg-gradient-to-br from-indigo-50 to-indigo-100 p-6 rounded-xl border border-indigo-200">
            <h4 class="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wide">Producer & Creator Information</h4>

            <!-- Producer -->
            <div class="mb-4 p-4 bg-white/70 rounded-lg border border-indigo-200/50">
              <h5 class="text-sm font-semibold text-indigo-900 mb-3">Producer (Author/Compiler)</h5>
              <div class="space-y-4">
                <div>
                  <label for="producer_name" class="block text-sm font-semibold text-gray-700 mb-2">Producer Name</label>
                  <input
                    type="text"
                    id="producer_name"
                    v-model="formData.producer_name"
                    class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                    placeholder="e.g., Monastero di San Colombano"
                  />
                </div>

                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label for="producer_type" class="block text-sm font-semibold text-gray-700 mb-2">Producer Type</label>
                    <select
                      id="producer_type"
                      v-model="formData.producer_type"
                      class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                    >
                      <option value="corporate">Corporate</option>
                      <option value="personal">Personal</option>
                    </select>
                  </div>

                  <div>
                    <label for="producer_role" class="block text-sm font-semibold text-gray-700 mb-2">Producer Role</label>
                    <input
                      type="text"
                      id="producer_role"
                      v-model="formData.producer_role"
                      class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                      placeholder="e.g., producer, author, compiler"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Creator -->
            <div class="p-4 bg-white/70 rounded-lg border border-indigo-200/50">
              <h5 class="text-sm font-semibold text-indigo-900 mb-3">Creator (Contributor)</h5>
              <div class="space-y-4">
                <div>
                  <label for="creator_name" class="block text-sm font-semibold text-gray-700 mb-2">Creator Name</label>
                  <input
                    type="text"
                    id="creator_name"
                    v-model="formData.creator_name"
                    class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                    placeholder="e.g., Giovanni Rossi"
                  />
                </div>

                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label for="creator_type" class="block text-sm font-semibold text-gray-700 mb-2">Creator Type</label>
                    <select
                      id="creator_type"
                      v-model="formData.creator_type"
                      class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                    >
                      <option value="personal">Personal</option>
                      <option value="corporate">Corporate</option>
                    </select>
                  </div>

                  <div>
                    <label for="creator_role" class="block text-sm font-semibold text-gray-700 mb-2">Creator Role</label>
                    <input
                      type="text"
                      id="creator_role"
                      v-model="formData.creator_role"
                      class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                      placeholder="e.g., creator, contributor, editor"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Rights Metadata Section -->
          <div class="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-xl border border-red-200">
            <h4 class="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wide">Rights Metadata (metsrights)</h4>
            <div class="space-y-5">
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label for="rights_category" class="block text-sm font-semibold text-gray-700 mb-2">Rights Category</label>
                  <select
                    id="rights_category"
                    v-model="formData.rights_category"
                    class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  >
                    <option value="">Select category</option>
                    <option value="COPYRIGHTED">COPYRIGHTED</option>
                    <option value="PUBLIC DOMAIN">PUBLIC DOMAIN</option>
                    <option value="CONTRACTUAL">CONTRACTUAL</option>
                    <option value="OTHER">OTHER</option>
                  </select>
                  <p class="mt-2 text-xs text-gray-500">Copyright status</p>
                </div>

                <div>
                  <label for="rights_holder" class="block text-sm font-semibold text-gray-700 mb-2">Rights Holder</label>
                  <input
                    type="text"
                    id="rights_holder"
                    v-model="formData.rights_holder"
                    class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                    placeholder="e.g., Archivio di Stato di Modena"
                  />
                  <p class="mt-2 text-xs text-gray-500">Organization/person holding rights</p>
                </div>
              </div>

              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label for="rights_constraint" class="block text-sm font-semibold text-gray-700 mb-2">Rights Constraint</label>
                  <input
                    type="text"
                    id="rights_constraint"
                    v-model="formData.rights_constraint"
                    class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                    placeholder="e.g., NoC-OKLR, InC, InC-EDU"
                  />
                  <p class="mt-2 text-xs text-gray-500">Rights statement code</p>
                </div>

                <div>
                  <label for="license_url" class="block text-sm font-semibold text-gray-700 mb-2">License URL</label>
                  <input
                    type="url"
                    id="license_url"
                    v-model="formData.license_url"
                    class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                    placeholder="https://creativecommons.org/..."
                  />
                  <p class="mt-2 text-xs text-gray-500">Link to license details</p>
                </div>
              </div>

              <div>
                <label for="rights_statement" class="block text-sm font-semibold text-gray-700 mb-2">Rights Statement</label>
                <textarea
                  id="rights_statement"
                  v-model="formData.rights_statement"
                  rows="2"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="Additional rights information"
                />
              </div>
            </div>
          </div>

          <!-- Technical Metadata Section -->
          <div class="border-b border-gray-200 pb-6">
            <h4 class="text-md font-medium text-gray-900 mb-4">Technical Metadata (Scanner/Image)</h4>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <label for="image_producer" class="block text-sm font-semibold text-gray-700 mb-2">Image Producer</label>
                <input
                  type="text"
                  id="image_producer"
                  v-model="formData.image_producer"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., EDS Gamma"
                />
              </div>

              <div>
                <label for="scanner_manufacturer" class="block text-sm font-semibold text-gray-700 mb-2">Scanner Manufacturer</label>
                <input
                  type="text"
                  id="scanner_manufacturer"
                  v-model="formData.scanner_manufacturer"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., Metis Systems srl"
                />
              </div>

              <div>
                <label for="scanner_model" class="block text-sm font-semibold text-gray-700 mb-2">Scanner Model</label>
                <input
                  type="text"
                  id="scanner_model"
                  v-model="formData.scanner_model"
                  class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
                  placeholder="e.g., DRS Scanner Model X"
                />
              </div>
            </div>
          </div>

          <!-- Record Status -->
          <div>
            <label for="record_status" class="block text-sm font-semibold text-gray-700 mb-2">Record Status</label>
            <select
              id="record_status"
              v-model="formData.record_status"
              class="block w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200"
            >
              <option value="COMPLETE">COMPLETE</option>
              <option value="MINIMUM">MINIMUM</option>
              <option value="REFERENCED">REFERENCED</option>
            </select>
            <p class="mt-2 text-xs text-gray-500">METS completion level (default: COMPLETE)</p>
          </div>
        </div>
      </div>

      <!-- Step 4: Review & Submit -->
      <div v-if="currentStep === 3" class="card-body">
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

        <!-- METS ECO-MiC Validation Section -->
        <div class="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <h4 class="text-sm font-medium text-green-900 mb-3">🔍 Validazione METS ECO-MiC</h4>
          <p class="text-sm text-green-700 mb-4">
            Verifica che i metadati siano conformi allo standard METS ECO-MiC 1.1 prima di completare l'upload.
          </p>
          
          <div v-if="!uploading" class="space-y-3">
            <!-- Debug info -->
            <div class="text-xs text-gray-500 mb-2">
              Debug: Step {{ currentStep }}, Uploading: {{ uploading }}, ValidatingMets: {{ validatingMets }}
            </div>
            
            <!-- Validation button -->
            <button
              @click="validateMetsXml"
              :disabled="validatingMets || uploading"
              class="inline-flex items-center px-4 py-2 border border-green-300 text-sm font-medium rounded-md text-green-800 bg-white hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <svg v-if="!validatingMets" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ validatingMets ? 'Validazione in corso...' : 'Verifica METS ECO-MiC' }}
            </button>

            <!-- Validation results -->
            <div v-if="metsValidationResult" class="mt-3">
              <!-- Success result -->
              <div v-if="metsValidationResult.valid" class="p-3 bg-green-100 rounded-lg border border-green-200">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-green-600 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-green-800">{{ metsValidationResult.summary }}</p>
                  </div>
                </div>
              </div>

              <!-- Error result -->
              <div v-else class="p-3 bg-red-100 rounded-lg border border-red-200">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-red-600 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-red-800 mb-2">{{ metsValidationResult.summary }}</p>
                    
                    <!-- Error details -->
                    <div v-if="metsValidationResult.errors.length > 0" class="space-y-2">
                      <p class="text-xs text-red-700 font-medium">Dettagli errori:</p>
                      <div class="max-h-32 overflow-y-auto space-y-1">
                        <div v-for="(error, index) in metsValidationResult.errors" :key="index" 
                             class="text-xs text-red-700 bg-red-50 p-2 rounded border">
                          <p><strong>Tipo:</strong> {{ error.type }}</p>
                          <p><strong>Descrizione:</strong> {{ error.description }}</p>
                          <p v-if="error.location !== 'N/A'"><strong>Posizione:</strong> {{ error.location }}</p>
                          <p v-if="error.tag !== 'N/A'"><strong>Tag:</strong> {{ error.tag }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Validation error -->
            <div v-if="metsValidationError" class="p-3 bg-red-100 rounded-lg border border-red-200">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-red-600 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p class="text-sm font-medium text-red-800">Errore durante la validazione</p>
                  <p class="text-xs text-red-700 mt-1">{{ metsValidationError }}</p>
                </div>
              </div>
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
      <div class="p-6 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
        <button
          v-if="currentStep > 0"
          @click="previousStep"
          :disabled="uploading"
          class="inline-flex items-center px-6 py-3 border-2 border-gray-300 text-base font-semibold rounded-xl text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-4 focus:ring-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm hover:shadow"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
          </svg>
          Previous
        </button>
        <div v-else></div>

        <div class="flex gap-3">
          <button
            @click="$emit('cancel')"
            :disabled="uploading"
            class="inline-flex items-center px-6 py-3 border-2 border-transparent text-base font-semibold rounded-xl text-gray-700 bg-gray-200 hover:bg-gray-300 focus:outline-none focus:ring-4 focus:ring-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm hover:shadow"
          >
            Cancel
          </button>

          <button
            v-if="currentStep < steps.length - 1"
            @click="nextStep"
            :disabled="!canProceedToNextStep || uploading"
            class="inline-flex items-center px-8 py-3 border-2 border-transparent text-base font-bold rounded-xl text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-4 focus:ring-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            Next Step
            <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            v-else
            @click="submitForm"
            :disabled="!canSubmit || uploading"
            class="inline-flex items-center px-8 py-3 border-2 border-transparent text-base font-bold rounded-xl text-white bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-4 focus:ring-green-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            <svg v-if="uploading" class="animate-spin -ml-1 mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ uploading ? 'Uploading...' : 'Create Document' }}
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
    
    // Metadata import state
    const selectedMetadataFile = ref(null)
    const metadataFileInput = ref(null)
    const metadataProcessing = ref(false)
    const metadataImported = ref(false)
    const metadataError = ref('')
    const importedFieldsCount = ref(0)

    // METS validation state
    const validatingMets = ref(false)
    const metsValidationResult = ref(null)
    const metsValidationError = ref('')

    // Steps configuration
    const steps = [
      { id: 'upload-basic', name: 'Upload & Basic Info' },
      { id: 'archive-context', name: 'Archive & Context' },
      { id: 'ecomic', name: 'ECO-MiC Metadata' },
      { id: 'review', name: 'Review & Submit' }
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
    // File handlers
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
      const supportedTypes = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/tiff',
        'image/x-adobe-dng',  // DNG format
        'image/dng',           // DNG alternate MIME type
        'application/pdf'
      ]

      // Check file types and sizes (DNG files can be up to 80GB, others 50MB)
      const validFiles = files.filter(file => {
        const isDNG = file.type === 'image/x-adobe-dng' || file.type === 'image/dng' || file.name.toLowerCase().endsWith('.dng')
        const maxSize = isDNG ? 80 * 1024 * 1024 * 1024 : 50 * 1024 * 1024  // 80GB for DNG, 50MB for others
        return (supportedTypes.includes(file.type) || isDNG) && file.size <= maxSize
      })

      if (validFiles.length !== files.length) {
        error.value = 'Some files were skipped. Only JPEG, PNG, TIFF, DNG, and PDF files are supported (DNG up to 80GB, others up to 50MB).'
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

    const removeImage = (index) => {
      selectedImages.value.splice(index, 1)
    }

    const clearFiles = () => {
      selectedFiles.value = []
      clearForm()
    }

    const clearImages = () => {
      selectedImages.value = []
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
        metadataError.value = err.message || 'Failed to process metadata file'
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
          throw new Error('Unsupported file format. Please use CSV or XML files.')
        }

        // Apply parsed data to form
        applyMetadataToForm(parsedData)
        
        metadataImported.value = true
        metadataProcessing.value = false
      } catch (err) {
        metadataProcessing.value = false
        throw err
      }
    }

    const readFileContent = (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target.result)
        reader.onerror = () => reject(new Error('Failed to read file'))
        reader.readAsText(file)
      })
    }

    const parseCSVMetadata = (csvContent) => {
      const lines = csvContent.trim().split('\n')
      if (lines.length < 2) {
        throw new Error('CSV file must have at least a header row and one data row')
      }

      const headers = lines[0].split(',').map(h => h.trim().replace(/['"]/g, ''))
      const values = lines[1].split(',').map(v => v.trim().replace(/['"]/g, ''))
      
      const data = {}
      headers.forEach((header, index) => {
        if (values[index] && values[index] !== '') {
          // Map CSV headers to form fields
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
        throw new Error('Invalid XML format')
      }

      const data = {}
      
      // Helper function to get text content from elements, handling namespaces better
      const getElementText = (tagName, attribute = null, attributeValue = null) => {
        // Try with namespace-aware approach first
        let elements = xmlDoc.getElementsByTagName(tagName)
        
        // If nothing found, try without namespace prefix
        if (elements.length === 0) {
          const localName = tagName.includes(':') ? tagName.split(':')[1] : tagName
          elements = xmlDoc.getElementsByTagName(localName)
        }
        
        // If still nothing, try searching all elements by local name
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

      // Helper function to get nested element text
      const getNestedElementText = (parentTag, childTag) => {
        const parents = xmlDoc.getElementsByTagName('*')
        
        for (let parent of parents) {
          const parentLocalName = parentTag.includes(':') ? parentTag.split(':')[1] : parentTag
          if (parent.localName === parentLocalName || parent.tagName.endsWith(':' + parentLocalName)) {
            const children = parent.getElementsByTagName('*')
            for (let child of children) {
              const childLocalName = childTag.includes(':') ? childTag.split(':')[1] : childTag
              if (child.localName === childLocalName || child.tagName.endsWith(':' + childLocalName)) {
                const text = child.textContent.trim()
                if (text) return text
              }
            }
          }
        }
        return null
      }

      // Try different field mappings with more flexible approach
      const fieldMappings = [
        // MODS identifier fields with namespace variations
        { getter: () => getElementText('mods:identifier', 'type', 'logical'), field: 'logical_id' },
        { getter: () => getElementText('identifier', 'type', 'logical'), field: 'logical_id' },
        { getter: () => getElementText('mods:identifier', 'type', 'conservative'), field: 'conservative_id' },
        { getter: () => getElementText('identifier', 'type', 'conservative'), field: 'conservative_id' },
        
        // Title - try both direct title and nested titleInfo/title
        { getter: () => getNestedElementText('mods:titleInfo', 'mods:title'), field: 'title' },
        { getter: () => getNestedElementText('titleInfo', 'title'), field: 'title' },
        { getter: () => getElementText('mods:title'), field: 'title' },
        { getter: () => getElementText('title'), field: 'title' },
        
        // Description/Abstract
        { getter: () => getElementText('mods:abstract'), field: 'description' },
        { getter: () => getElementText('abstract'), field: 'description' },
        { getter: () => getElementText('dc:description'), field: 'description' },
        { getter: () => getElementText('description'), field: 'description' },
        
        // Document type
        { getter: () => getElementText('mods:typeOfResource'), field: 'document_type' },
        { getter: () => getElementText('typeOfResource'), field: 'document_type' },
        { getter: () => getElementText('dc:type'), field: 'document_type' },
        { getter: () => getElementText('type'), field: 'document_type' },
        
        // Archive/Institution name
        { getter: () => getNestedElementText('mods:name', 'mods:namePart'), field: 'archive_name' },
        { getter: () => getNestedElementText('name', 'namePart'), field: 'archive_name' },
        { getter: () => getElementText('mods:namePart'), field: 'archive_name' },
        { getter: () => getElementText('namePart'), field: 'archive_name' },
        { getter: () => getElementText('dc:publisher'), field: 'archive_name' },
        { getter: () => getElementText('publisher'), field: 'archive_name' },
        
        // Physical description
        { getter: () => getNestedElementText('mods:physicalDescription', 'mods:extent'), field: 'total_pages' },
        { getter: () => getNestedElementText('physicalDescription', 'extent'), field: 'total_pages' },
        { getter: () => getElementText('mods:extent'), field: 'total_pages' },
        { getter: () => getElementText('extent'), field: 'total_pages' },
        
        // Dates
        { getter: () => getElementText('mods:dateCreated', 'point', 'start'), field: 'date_from' },
        { getter: () => getElementText('dateCreated', 'point', 'start'), field: 'date_from' },
        { getter: () => getElementText('mods:dateCreated', 'point', 'end'), field: 'date_to' },
        { getter: () => getElementText('dateCreated', 'point', 'end'), field: 'date_to' },
        { getter: () => getElementText('mods:dateCreated'), field: 'date_from' },
        { getter: () => getElementText('dateCreated'), field: 'date_from' },
        { getter: () => getElementText('dc:date'), field: 'date_from' },
        { getter: () => getElementText('date'), field: 'date_from' },
        
        // Location
        { getter: () => getNestedElementText('mods:place', 'mods:placeTerm'), field: 'location' },
        { getter: () => getNestedElementText('place', 'placeTerm'), field: 'location' },
        { getter: () => getElementText('mods:placeTerm'), field: 'location' },
        { getter: () => getElementText('placeTerm'), field: 'location' },
        { getter: () => getElementText('dc:coverage'), field: 'location' },
        { getter: () => getElementText('coverage'), field: 'location' },
        
        // Language
        { getter: () => getNestedElementText('mods:language', 'mods:languageTerm'), field: 'language' },
        { getter: () => getNestedElementText('language', 'languageTerm'), field: 'language' },
        { getter: () => getElementText('mods:languageTerm'), field: 'language' },
        { getter: () => getElementText('languageTerm'), field: 'language' },
        { getter: () => getElementText('dc:language'), field: 'language' },
        { getter: () => getElementText('language'), field: 'language' },
        
        // Subjects
        { getter: () => getNestedElementText('mods:subject', 'mods:topic'), field: 'subjects' },
        { getter: () => getNestedElementText('subject', 'topic'), field: 'subjects' },
        { getter: () => getElementText('mods:topic'), field: 'subjects' },
        { getter: () => getElementText('topic'), field: 'subjects' },
        { getter: () => getElementText('dc:subject'), field: 'subjects' },
        { getter: () => getElementText('subject'), field: 'subjects' },
        
        // Dublin Core fallbacks
        { getter: () => getElementText('dc:identifier'), field: 'logical_id' },
        { getter: () => getElementText('dc:creator'), field: 'archive_name' }
      ]

      fieldMappings.forEach(({ getter, field }) => {
        try {
          const value = getter()
          if (value && value !== '' && !data[field]) {
            // Convert some common mappings
            if (field === 'document_type') {
              const typeMap = {
                'text': 'manuscript',
                'still image': 'photograph',
                'image': 'photograph',
                'cartographic': 'map',
                'notated music': 'document'
              }
              data[field] = typeMap[value.toLowerCase()] || value
            } else if (field === 'total_pages') {
              // Extract numbers from extent field
              const match = value.match(/(\d+)/)
              if (match) {
                data[field] = parseInt(match[1])
              }
            } else if (field === 'language') {
              // Convert language codes
              const langMap = {
                'ita': 'it',
                'eng': 'en', 
                'lat': 'la',
                'fra': 'fr',
                'deu': 'de',
                'spa': 'es',
                'italian': 'it',
                'english': 'en',
                'latin': 'la',
                'french': 'fr',
                'german': 'de',
                'spanish': 'es'
              }
              data[field] = langMap[value.toLowerCase()] || value
            } else {
              data[field] = value
            }
          }
        } catch (e) {
          console.warn(`Error processing field ${field}:`, e)
        }
      })

      // Try to get related items for fund and series with better namespace handling
      try {
        const allElements = xmlDoc.getElementsByTagName('*')
        for (let item of allElements) {
          if (item.localName === 'relatedItem' || item.tagName.includes('relatedItem')) {
            const type = item.getAttribute('type')
            // Look for title within this relatedItem
            const titleElements = item.getElementsByTagName('*')
            for (let titleEl of titleElements) {
              if ((titleEl.localName === 'title' || titleEl.tagName.includes('title')) && titleEl.textContent.trim()) {
                const titleText = titleEl.textContent.trim()
                if (type === 'host' && !data.fund_name) {
                  data.fund_name = titleText
                } else if (type === 'series' && !data.series_name) {
                  data.series_name = titleText
                }
              }
            }
          }
        }
      } catch (e) {
        console.warn('Error processing related items:', e)
      }

      // Debug: log what we found
      console.log('Parsed XML data:', data)

      return data
    }

    const mapHeaderToField = (header) => {
      // Normalize header name
      const normalizedHeader = header.toLowerCase().replace(/[^a-z0-9]/g, '_')
      
      // Map common CSV headers to form fields
      const headerMappings = {
        'logical_id': 'logical_id',
        'logicalid': 'logical_id',
        'id': 'logical_id',
        'identifier': 'logical_id',
        'conservative_id': 'conservative_id',
        'conservativeid': 'conservative_id',
        'archive_id': 'conservative_id',
        'title': 'title',
        'name': 'title',
        'description': 'description',
        'summary': 'description',
        'archive_name': 'archive_name',
        'archivename': 'archive_name',
        'archive': 'archive_name',
        'institution': 'archive_name',
        'archive_contact': 'archive_contact',
        'contact': 'archive_contact',
        'email': 'archive_contact',
        'fund_name': 'fund_name',
        'fundname': 'fund_name',
        'fund': 'fund_name',
        'collection': 'fund_name',
        'series_name': 'series_name',
        'seriesname': 'series_name',
        'series': 'series_name',
        'folder_number': 'folder_number',
        'foldernumber': 'folder_number',
        'folder': 'folder_number',
        'unit': 'folder_number',
        'busta': 'folder_number',
        'document_type': 'document_type',
        'documenttype': 'document_type',
        'type': 'document_type',
        'total_pages': 'total_pages',
        'totalpages': 'total_pages',
        'pages': 'total_pages',
        'page_count': 'total_pages',
        'date_from': 'date_from',
        'datefrom': 'date_from',
        'start_date': 'date_from',
        'date_start': 'date_from',
        'date': 'date_from',
        'date_to': 'date_to',
        'dateto': 'date_to',
        'end_date': 'date_to',
        'date_end': 'date_to',
        'period': 'period',
        'era': 'period',
        'epoch': 'period',
        'location': 'location',
        'place': 'location',
        'geographic': 'location',
        'language': 'language',
        'lang': 'language',
        'subjects': 'subjects',
        'keywords': 'subjects',
        'subject': 'subjects',
        'tags': 'subjects',
        'conservative_id_authority': 'conservative_id_authority',
        'authority': 'conservative_id_authority',
        'id_authority': 'conservative_id_authority'
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
        throw new Error('No matching fields found in the metadata file. Please check the field names.')
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

    const validateMetsXml = async () => {
      validatingMets.value = true
      metsValidationResult.value = null
      metsValidationError.value = ''

      try {
        // Prepare form data for validation
        const validationData = {
          logical_id: formData.logical_id,
          title: formData.title,
          description: formData.description,
          conservative_id: formData.conservative_id,
          conservative_id_authority: formData.conservative_id_authority,
          archive_name: formData.archive_name,
          archive_contact: formData.archive_contact,
          license_url: formData.license_url,
          rights_statement: formData.rights_statement,
          image_producer: formData.image_producer,
          scanner_manufacturer: formData.scanner_manufacturer,
          scanner_model: formData.scanner_model,
          document_type: formData.document_type,
          total_pages: formData.total_pages,
          date_from: formData.date_from,
          date_to: formData.date_to,
          period: formData.period,
          location: formData.location,
          language: formData.language,
          subjects: formData.subjects,
          fund_name: formData.fund_name,
          series_name: formData.series_name,
          folder_number: formData.folder_number
        }

        // Remove null/undefined values
        Object.keys(validationData).forEach(key => {
          if (validationData[key] === null || validationData[key] === undefined || validationData[key] === '') {
            delete validationData[key]
          }
        })

        // VALIDATION DISABLED - endpoint not available
        // Skip validation for now
        metsValidationResult.value = {
          valid: true,
          summary: 'Validation skipped (endpoint disabled)',
          errors: []
        }

      } catch (err) {
        console.error('METS validation error:', err)
        if (err.response?.data?.detail) {
          metsValidationError.value = err.response.data.detail
        } else {
          metsValidationError.value = 'Errore durante la validazione METS ECO-MiC. Riprova più tardi.'
        }
      } finally {
        validatingMets.value = false
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
        // STEP 1: Create the document with metadata (using first file)
        uploadStatus.value = 'Creating document...'
        const firstFileFormData = new FormData()
        firstFileFormData.append('file', selectedFiles.value[0])

        // Add all metadata fields (use original logical_id, no suffix!)
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
              uploadStatus.value = `Creating document... ${fileProgress}%`
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

            uploadStatus.value = `Uploading ${file.name}... (${i + 2}/${selectedFiles.value.length})`

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
                  uploadStatus.value = `Uploading ${file.name}... ${fileProgress}%`
                }
              }
            )
          }
        }

        uploadStatus.value = 'Upload complete!'
        uploadProgress.value = 100

        setTimeout(() => {
          emit('upload-complete', {
            documents: [createdDocument],
            count: 1  // Always 1 document, even with multiple files
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
      
      // Metadata import state
      selectedMetadataFile,
      metadataFileInput,
      metadataProcessing,
      metadataImported,
      metadataError,
      importedFieldsCount,
      
      // METS validation state
      validatingMets,
      metsValidationResult,
      metsValidationError,
      
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
      
      // Metadata import methods
      triggerMetadataFileInput,
      handleMetadataFileSelect,
      clearMetadataFile,
      
      // METS validation methods
      validateMetsXml,
      
      submitForm
    }
  }
}
</script>
