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

        <!-- Metadata Import Section -->
        <div class="mb-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
          <h4 class="text-md font-medium text-blue-900 mb-3">📋 Optional: Import METS Metadata</h4>
          <p class="text-sm text-blue-700 mb-4">Upload a CSV or XML file with METS fields to pre-fill the form automatically</p>
          
          <!-- Metadata file input -->
          <div class="flex items-center space-x-4">
            <button
              @click="triggerMetadataFileInput"
              type="button"
              class="inline-flex items-center px-4 py-2 border border-blue-300 shadow-sm text-sm font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              Choose Metadata File
            </button>
            
            <div v-if="selectedMetadataFile" class="flex items-center space-x-2 text-sm">
              <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span class="text-green-700 font-medium">{{ selectedMetadataFile.name }}</span>
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

        <!-- Document Upload Section -->
        <div class="space-y-6">
          <div>
            <h4 class="text-md font-medium text-gray-900 mb-4">Document Files</h4>
            <div 
              @drop="handleDocumentDrop"
              @dragover.prevent
              @dragenter.prevent="isDocumentDragOver = true"
              @dragleave.prevent="isDocumentDragOver = false"
              @click="triggerDocumentInput"
              :class="[
                'relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
                isDocumentDragOver 
                  ? 'border-blue-400 bg-blue-50' 
                  : selectedFiles.length 
                  ? 'border-green-400 bg-green-50' 
                  : 'border-gray-300 hover:border-gray-400'
              ]"
            >
              <input
                ref="fileInput"
                type="file"
                @change="handleDocumentSelect"
                accept="image/*,.pdf"
                class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                multiple
              />

              <div v-if="!selectedFiles.length">
                <svg class="mx-auto h-10 w-10 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <p class="mt-2 text-sm text-gray-600">
                  <span class="font-medium text-blue-600">Click to upload</span> or drag and drop document files
                </p>
                <p class="text-xs text-gray-500">PNG, JPG, TIFF, PDF up to 50MB each</p>
              </div>

              <div v-else class="space-y-3">
                <svg class="mx-auto h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ selectedFiles.length }} document file(s) selected</p>
                  <div class="mt-2 space-y-2">
                    <div v-for="(file, index) in selectedFiles" :key="file.name" class="flex items-center justify-between bg-white rounded p-2 text-xs">
                      <div class="flex items-center space-x-2">
                        <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2v12a2 2 0 002 2z" />
                        </svg>
                        <div>
                          <p class="font-medium text-gray-900">{{ file.name }}</p>
                          <p class="text-gray-500">{{ formatFileSize(file.size) }}</p>
                        </div>
                      </div>
                      <button
                        @click.stop="removeFile(index)"
                        class="text-red-500 hover:text-red-700"
                      >
                        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
                <button
                  @click.stop="clearFiles"
                  class="text-xs text-gray-500 hover:text-gray-700"
                >
                  Clear all files
                </button>
              </div>
            </div>
          </div>

          <!-- Optional Images Section -->
          <div>
            <h4 class="text-md font-medium text-gray-900 mb-2">Additional Images (Optional)</h4>
            <p class="text-sm text-gray-500 mb-4">Upload additional images related to this document (photos, scans, etc.)</p>
            
            <div 
              @drop="handleImageDrop"
              @dragover.prevent
              @dragenter.prevent="isImageDragOver = true"
              @dragleave.prevent="isImageDragOver = false"
              @click="triggerImageInput"
              :class="[
                'relative border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors',
                isImageDragOver 
                  ? 'border-purple-400 bg-purple-50' 
                  : selectedImages.length 
                  ? 'border-purple-400 bg-purple-50' 
                  : 'border-gray-300 hover:border-gray-400'
              ]"
            >
              <input
                ref="imageInput"
                type="file"
                @change="handleImageSelect"
                accept="image/*"
                class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                multiple
              />

              <div v-if="!selectedImages.length">
                <svg class="mx-auto h-8 w-8 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2v12a2 2 0 002 2z" />
                </svg>
                <p class="mt-2 text-sm text-gray-600">
                  <span class="font-medium text-purple-600">Click to upload</span> or drag images here
                </p>
                <p class="text-xs text-gray-500">JPG, PNG, TIFF up to 20MB each</p>
              </div>

              <div v-else class="space-y-2">
                <svg class="mx-auto h-6 w-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-sm font-medium text-gray-900">{{ selectedImages.length }} image(s) selected</p>
                <div class="grid grid-cols-2 gap-2 mt-2">
                  <div v-for="(image, index) in selectedImages" :key="image.name" class="relative bg-white rounded border p-2">
                    <div class="flex items-center space-x-2">
                      <div class="w-8 h-8 bg-purple-100 rounded flex items-center justify-center">
                        <svg class="h-4 w-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-xs font-medium text-gray-900 truncate">{{ image.name }}</p>
                        <p class="text-xs text-gray-500">{{ formatFileSize(image.size) }}</p>
                      </div>
                      <button
                        @click.stop="removeImage(index)"
                        class="text-red-500 hover:text-red-700"
                      >
                        <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
                <button
                  @click.stop="clearImages"
                  class="text-xs text-purple-600 hover:text-purple-700"
                >
                  Clear all images
                </button>
              </div>
            </div>
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
    const selectedImages = ref([])
    const isDragOver = ref(false)
    const isDocumentDragOver = ref(false)
    const isImageDragOver = ref(false)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const error = ref('')
    const fileInput = ref(null)
    const imageInput = ref(null)
    
    // Metadata import state
    const selectedMetadataFile = ref(null)
    const metadataFileInput = ref(null)
    const metadataProcessing = ref(false)
    const metadataImported = ref(false)
    const metadataError = ref('')
    const importedFieldsCount = ref(0)

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
    // Document file handlers
    const triggerDocumentInput = () => {
      fileInput.value?.click()
    }

    const handleDocumentSelect = (event) => {
      const files = Array.from(event.target.files)
      addDocumentFiles(files)
    }

    const handleDocumentDrop = (event) => {
      event.preventDefault()
      isDocumentDragOver.value = false
      const files = Array.from(event.dataTransfer.files)
      addDocumentFiles(files)
    }

    const addDocumentFiles = (files) => {
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

    // Image file handlers
    const triggerImageInput = () => {
      imageInput.value?.click()
    }

    const handleImageSelect = (event) => {
      const files = Array.from(event.target.files)
      addImageFiles(files)
    }

    const handleImageDrop = (event) => {
      event.preventDefault()
      isImageDragOver.value = false
      const files = Array.from(event.dataTransfer.files)
      addImageFiles(files)
    }

    const addImageFiles = (files) => {
      // Filter for supported image types only
      const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff']
      const validFiles = files.filter(file => 
        supportedTypes.includes(file.type) && file.size <= 20 * 1024 * 1024 // 20MB limit for images
      )

      if (validFiles.length !== files.length) {
        error.value = 'Some image files were skipped. Only JPEG, PNG, and TIFF files under 20MB are supported.'
      } else {
        error.value = ''
      }

      // Add valid files to selection
      selectedImages.value.push(...validFiles)
    }

    // Legacy handlers for compatibility
    const handleFileSelect = handleDocumentSelect
    const handleDrop = handleDocumentDrop
    const triggerFileInput = triggerDocumentInput

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
        const allUploads = []
        
        // Upload document files first
        const documentPromises = selectedFiles.value.map(async (file, index) => {
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

          uploadStatus.value = `Uploading document ${file.name}...`
          
          return {
            type: 'document',
            promise: axios.post(
              `${import.meta.env.VITE_API_URL}/api/documents/upload`,
              formDataToSend,
              {
                headers: {
                  'Authorization': `Bearer ${authStore.token}`,
                  'Content-Type': 'multipart/form-data'
                },
                onUploadProgress: (progressEvent) => {
                  const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                  const totalFiles = selectedFiles.value.length + selectedImages.value.length
                  const overallProgress = Math.round(((index * 100) + fileProgress) / totalFiles)
                  uploadProgress.value = overallProgress
                  uploadStatus.value = `Uploading document ${file.name}... ${fileProgress}%`
                }
              }
            )
          }
        })

        // Add document uploads to queue
        allUploads.push(...documentPromises)

        // Upload additional images if any
        if (selectedImages.value.length > 0) {
          const imagePromises = selectedImages.value.map(async (image, index) => {
            uploadStatus.value = `Uploading image ${image.name}...`
            
            return {
              type: 'image',
              promise: axios.post(
                `${import.meta.env.VITE_API_URL}/api/files/upload-image`,
                { 
                  file: image, 
                  logical_id: formData.logical_id,
                  image_type: 'additional' 
                },
                {
                  headers: {
                    'Authorization': `Bearer ${authStore.token}`,
                    'Content-Type': 'multipart/form-data'
                  },
                  onUploadProgress: (progressEvent) => {
                    const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                    const totalFiles = selectedFiles.value.length + selectedImages.value.length
                    const baseIndex = selectedFiles.value.length + index
                    const overallProgress = Math.round(((baseIndex * 100) + fileProgress) / totalFiles)
                    uploadProgress.value = overallProgress
                    uploadStatus.value = `Uploading image ${image.name}... ${fileProgress}%`
                  }
                }
              )
            }
          })
          
          // Add image uploads to queue
          allUploads.push(...imagePromises)
        }

        // Execute all uploads
        const responses = await Promise.all(allUploads.map(upload => upload.promise))
        
        uploadStatus.value = 'Upload complete!'
        uploadProgress.value = 100
        
        setTimeout(() => {
          const documentResponses = responses.slice(0, selectedFiles.value.length)
          const imageResponses = responses.slice(selectedFiles.value.length)
          
          emit('upload-complete', {
            documents: documentResponses.map(r => r.data),
            images: imageResponses.map(r => r.data),
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
      selectedImages,
      isDragOver,
      isDocumentDragOver,
      isImageDragOver,
      uploading,
      uploadProgress,
      uploadStatus,
      error,
      fileInput,
      imageInput,
      
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
      
      // Document file methods
      triggerDocumentInput,
      handleDocumentSelect,
      handleDocumentDrop,
      removeFile,
      clearFiles,
      
      // Image file methods
      triggerImageInput,
      handleImageSelect,
      handleImageDrop,
      removeImage,
      clearImages,
      
      // Legacy methods for compatibility
      triggerFileInput,
      handleFileSelect,
      handleDrop,
      
      // General methods
      formatFileSize,
      nextStep,
      previousStep,
      
      // Metadata import methods
      triggerMetadataFileInput,
      handleMetadataFileSelect,
      clearMetadataFile,
      
      submitForm
    }
  }
}
</script>
