<template>
  <!-- Document Detail Modal -->
  <TransitionRoot appear :show="!!document" as="template">
    <Dialog as="div" @close="!showFileDetail && closeModal()" class="relative z-50" :static="showFileDetail">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-50" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-7xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
              <!-- Header -->
              <div class="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
                <div>
                  <DialogTitle as="h3" class="text-2xl font-bold leading-6 text-gray-900">
                    {{ document?.title || document?.logical_id || 'Document Details' }}
                  </DialogTitle>
                  <p class="mt-2 text-sm text-gray-600 flex items-center gap-2">
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    <span class="font-medium">ID:</span> {{ document?.logical_id }}
                  </p>
                </div>
                <div class="flex items-center space-x-2">
                  <button
                    v-if="!isEditing"
                    @click="startEdit"
                    class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    Edit
                  </button>
                  
                  <div v-if="isEditing" class="flex items-center space-x-2">
                    <button
                      @click="saveChanges"
                      :disabled="saving"
                      class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                    >
                      <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      {{ saving ? 'Saving...' : 'Save' }}
                    </button>
                    <button
                      @click="deleteDocument"
                      :disabled="deleting"
                      class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                    >
                      <svg v-if="deleting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      {{ deleting ? 'Deleting...' : 'Delete' }}
                    </button>
                    <button
                      @click="cancelEdit"
                      :disabled="saving || deleting"
                      class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                      Cancel
                    </button>
                  </div>
                  
                  <button
                    @click="closeModal"
                    class="rounded-md bg-white text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Tab Navigation -->
              <div class="border-b border-gray-200 bg-gray-50">
                <nav class="flex -mb-px px-6" aria-label="Tabs">
                  <button
                    @click="activeTab = 'overview'"
                    :class="[
                      'whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm transition-colors',
                      activeTab === 'overview'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    ]"
                  >
                    <div class="flex items-center gap-2">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Overview
                    </div>
                  </button>
                  <button
                    @click="activeTab = 'archive'"
                    :class="[
                      'whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm transition-colors',
                      activeTab === 'archive'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    ]"
                  >
                    <div class="flex items-center gap-2">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                      </svg>
                      Archive Info
                    </div>
                  </button>
                  <button
                    @click="activeTab = 'files'"
                    :class="[
                      'whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm transition-colors',
                      activeTab === 'files'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    ]"
                  >
                    <div class="flex items-center gap-2">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      Files ({{ document?.document_files?.length || 0 }})
                    </div>
                  </button>
                </nav>
              </div>

              <!-- Tab Content -->
              <div class="h-[550px] overflow-y-auto">
                <!-- Overview Tab -->
                <div v-if="activeTab === 'overview'" class="p-8">
                  
                  <!-- Display Mode -->
                  <div v-if="!isEditing" class="space-y-4">
                    <div v-if="document?.logical_id" class="flex">
                      <dt class="w-1/3 text-sm font-medium text-gray-500">Logical ID:</dt>
                      <dd class="text-sm text-gray-900">{{ document.logical_id }}</dd>
                    </div>
                    <div v-if="document?.conservative_id" class="flex">
                      <dt class="w-1/3 text-sm font-medium text-gray-500">Conservative ID:</dt>
                      <dd class="text-sm text-gray-900">{{ document.conservative_id }}</dd>
                    </div>
                    <div v-if="document?.title" class="flex">
                      <dt class="w-1/3 text-sm font-medium text-gray-500">Title:</dt>
                      <dd class="text-sm text-gray-900">{{ document.title }}</dd>
                    </div>
                    <div v-if="document?.description" class="flex">
                      <dt class="w-1/3 text-sm font-medium text-gray-500">Description:</dt>
                      <dd class="text-sm text-gray-900">{{ document.description }}</dd>
                    </div>
                    <div v-if="document?.archive_name" class="flex">
                      <dt class="w-1/3 text-sm font-medium text-gray-500">Archive:</dt>
                      <dd class="text-sm text-gray-900">{{ document.archive_name }}</dd>
                    </div>
                    <div v-if="document?.document_type" class="flex">
                      <dt class="w-1/3 text-sm font-medium text-gray-500">Type:</dt>
                      <dd class="text-sm text-gray-900">{{ document.document_type }}</dd>
                    </div>
                    <div v-if="document?.total_pages" class="flex">
                      <dt class="w-1/3 text-sm font-medium text-gray-500">Pages:</dt>
                      <dd class="text-sm text-gray-900">{{ document.total_pages }}</dd>
                    </div>
                    <div v-if="document?.created_at" class="flex">
                      <dt class="w-1/3 text-sm font-medium text-gray-500">Created:</dt>
                      <dd class="text-sm text-gray-900">{{ formatDate(document.created_at) }}</dd>
                    </div>
                  </div>

                  <!-- Edit Mode -->
                  <div v-else class="space-y-8">
                    <!-- Image Upload Section -->
                    <div class="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                      <h4 class="text-lg font-medium text-gray-900 mb-4">🖼️ Document Image</h4>
                      
                      <!-- Current Image Preview -->
                      <div v-if="imageFiles.length > 0" class="mb-4">
                        <p class="text-sm text-gray-600 mb-2">Current image:</p>
                        <div class="relative inline-block">
                          <div 
                            v-if="selectedFile && selectedFile.file_id === imageFiles[0].file_id && imageDataUrl && imageLoaded"
                            class="h-32 w-auto"
                          >
                            <img 
                              :src="imageDataUrl" 
                              :alt="imageFiles[0].filename"
                              class="h-32 w-auto object-contain rounded border border-gray-200"
                            />
                          </div>
                          <div 
                            v-else 
                            class="h-32 w-32 bg-gray-100 rounded border border-gray-200 flex items-center justify-center"
                          >
                            <svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2v12a2 2 0 002 2z" />
                            </svg>
                          </div>
                          <div class="mt-1 text-xs text-gray-500">{{ imageFiles[0].filename }}</div>
                        </div>
                      </div>
                      
                      <!-- Image Upload Drop Zone -->
                      <div 
                        @drop="handleImageDrop"
                        @dragover.prevent
                        @dragenter.prevent="isImageDragOver = true"
                        @dragleave.prevent="isImageDragOver = false"
                        @click="triggerImageInput"
                        :class="[
                          'relative border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors',
                          isImageDragOver 
                            ? 'border-blue-400 bg-blue-50' 
                            : 'border-gray-300 hover:border-gray-400'
                        ]"
                      >
                        <input
                          ref="imageInput"
                          type="file"
                          @change="handleImageSelect"
                          accept="image/*"
                          class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        />
                        
                        <div class="flex flex-col items-center">
                          <svg class="h-8 w-8 text-gray-400 mb-2" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                          </svg>
                          <span class="text-sm text-gray-600">
                            {{ imageFiles.length > 0 ? 'Click to replace image' : 'Click to upload image' }}
                          </span>
                          <span class="text-xs text-gray-500 mt-1">PNG, JPG, TIFF up to 50MB</span>
                        </div>
                      </div>
                      
                      <!-- Upload Progress -->
                      <div v-if="imageUploading" class="mt-3">
                        <div class="flex items-center">
                          <svg class="animate-spin h-4 w-4 text-blue-600 mr-2" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          <span class="text-sm text-blue-800">Uploading image...</span>
                        </div>
                        <div class="w-full bg-blue-200 rounded-full h-1 mt-2">
                          <div 
                            class="bg-blue-600 h-1 rounded-full transition-all duration-300" 
                            :style="{ width: imageUploadProgress + '%' }"
                          ></div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Basic Information Section -->
                    <div class="bg-gray-50 p-4 rounded-lg">
                      <h4 class="text-lg font-medium text-gray-900 mb-4">📄 Basic Information</h4>
                      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div class="sm:col-span-2">
                          <label for="edit-logical-id" class="block text-sm font-medium text-gray-700">Logical ID *</label>
                          <input
                            type="text"
                            id="edit-logical-id"
                            v-model="editForm.logical_id"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="Unique document identifier"
                            required
                          />
                        </div>
                        <div>
                          <label for="edit-conservative-id" class="block text-sm font-medium text-gray-700">Conservative ID</label>
                          <input
                            type="text"
                            id="edit-conservative-id"
                            v-model="editForm.conservative_id"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., IT-MO0172"
                          />
                        </div>
                        <div>
                          <label for="edit-conservative-authority" class="block text-sm font-medium text-gray-700">ID Authority</label>
                          <input
                            type="text"
                            id="edit-conservative-authority"
                            v-model="editForm.conservative_id_authority"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., ISIL"
                          />
                        </div>
                        <div class="sm:col-span-2">
                          <label for="edit-title" class="block text-sm font-medium text-gray-700">Title</label>
                          <input
                            type="text"
                            id="edit-title"
                            v-model="editForm.title"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="Enter document title"
                          />
                        </div>
                        <div class="sm:col-span-2">
                          <label for="edit-description" class="block text-sm font-medium text-gray-700">Description</label>
                          <textarea
                            id="edit-description"
                            v-model="editForm.description"
                            rows="3"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="Enter document description"
                          ></textarea>
                        </div>
                        <div>
                          <label for="edit-type" class="block text-sm font-medium text-gray-700">Document Type</label>
                          <select
                            id="edit-type"
                            v-model="editForm.document_type"
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
                          <label for="edit-pages" class="block text-sm font-medium text-gray-700">Total Pages</label>
                          <input
                            type="number"
                            id="edit-pages"
                            v-model.number="editForm.total_pages"
                            min="1"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="Number of pages"
                          />
                        </div>
                      </div>
                    </div>

                    <!-- Archive Information Section -->
                    <div class="bg-blue-50 p-4 rounded-lg">
                      <h4 class="text-lg font-medium text-gray-900 mb-4">🏛️ Archive Information</h4>
                      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div class="sm:col-span-2">
                          <label for="edit-archive-name" class="block text-sm font-medium text-gray-700">Archive Name</label>
                          <input
                            type="text"
                            id="edit-archive-name"
                            v-model="editForm.archive_name"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., Archivio di Stato di Modena"
                          />
                        </div>
                        <div class="sm:col-span-2">
                          <label for="edit-archive-contact" class="block text-sm font-medium text-gray-700">Archive Contact</label>
                          <input
                            type="email"
                            id="edit-archive-contact"
                            v-model="editForm.archive_contact"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., as-mo@cultura.gov.it"
                          />
                        </div>
                        <div>
                          <label for="edit-fund-name" class="block text-sm font-medium text-gray-700">Fund Name</label>
                          <input
                            type="text"
                            id="edit-fund-name"
                            v-model="editForm.fund_name"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., Fondo Fotografico"
                          />
                        </div>
                        <div>
                          <label for="edit-series-name" class="block text-sm font-medium text-gray-700">Series Name</label>
                          <input
                            type="text"
                            id="edit-series-name"
                            v-model="editForm.series_name"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., Serie I"
                          />
                        </div>
                        <div class="sm:col-span-2">
                          <label for="edit-folder-number" class="block text-sm font-medium text-gray-700">Folder/Unit Number</label>
                          <input
                            type="text"
                            id="edit-folder-number"
                            v-model="editForm.folder_number"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., Busta 45"
                          />
                        </div>
                      </div>
                    </div>

                    <!-- Temporal and Contextual Information Section -->
                    <div class="bg-green-50 p-4 rounded-lg">
                      <h4 class="text-lg font-medium text-gray-900 mb-4">📅 Temporal & Contextual Information</h4>
                      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                          <label for="edit-date-from" class="block text-sm font-medium text-gray-700">Date From</label>
                          <input
                            type="date"
                            id="edit-date-from"
                            v-model="editForm.date_from"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                          />
                        </div>
                        <div>
                          <label for="edit-date-to" class="block text-sm font-medium text-gray-700">Date To</label>
                          <input
                            type="date"
                            id="edit-date-to"
                            v-model="editForm.date_to"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                          />
                        </div>
                        <div>
                          <label for="edit-period" class="block text-sm font-medium text-gray-700">Historical Period</label>
                          <input
                            type="text"
                            id="edit-period"
                            v-model="editForm.period"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., Renaissance, 20th Century"
                          />
                        </div>
                        <div>
                          <label for="edit-location" class="block text-sm font-medium text-gray-700">Location</label>
                          <input
                            type="text"
                            id="edit-location"
                            v-model="editForm.location"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., Modena, Italy"
                          />
                        </div>
                        <div>
                          <label for="edit-language" class="block text-sm font-medium text-gray-700">Language</label>
                          <select
                            id="edit-language"
                            v-model="editForm.language"
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
                          <label for="edit-subjects" class="block text-sm font-medium text-gray-700">Subjects/Keywords</label>
                          <input
                            type="text"
                            id="edit-subjects"
                            v-model="editForm.subjects"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="e.g., architecture, portrait, landscape"
                          />
                          <p class="mt-1 text-xs text-gray-500">Separate multiple subjects with commas</p>
                        </div>
                      </div>
                    </div>

                    <!-- ECO-MiC Metadata Section -->
                    <div class="bg-purple-50 p-4 rounded-lg">
                      <h4 class="text-lg font-medium text-gray-900 mb-4">📋 ECO-MiC 1.2 Metadata</h4>
                      <p class="text-xs text-gray-500 mb-4">Optional fields for METS ECO-MiC compliance</p>

                      <div class="space-y-4">
                        <!-- Resource Type & Physical Description -->
                        <div class="border-b border-purple-200 pb-4">
                          <h5 class="text-sm font-semibold text-gray-900 mb-3">Resource Type & Physical Description</h5>
                          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                            <div>
                              <label for="edit-type-of-resource" class="block text-xs font-medium text-gray-700">Type of Resource</label>
                              <select
                                id="edit-type-of-resource"
                                v-model="editForm.type_of_resource"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                              >
                                <option value="">Select type</option>
                                <option value="risorsa manoscritta">Risorsa manoscritta</option>
                                <option value="documento testuale">Documento testuale</option>
                                <option value="documento cartografico">Documento cartografico</option>
                                <option value="documento fotografico">Documento fotografico</option>
                                <option value="documento grafico">Documento grafico</option>
                                <option value="risorsa a stampa">Risorsa a stampa</option>
                              </select>
                            </div>
                            <div>
                              <label for="edit-physical-form" class="block text-xs font-medium text-gray-700">Physical Form</label>
                              <input
                                type="text"
                                id="edit-physical-form"
                                v-model="editForm.physical_form"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., documento testuale"
                              />
                            </div>
                            <div class="sm:col-span-2">
                              <label for="edit-extent-description" class="block text-xs font-medium text-gray-700">Extent Description</label>
                              <input
                                type="text"
                                id="edit-extent-description"
                                v-model="editForm.extent_description"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., c. 14 nel fascicolo"
                              />
                            </div>
                          </div>
                        </div>

                        <!-- Producer Information -->
                        <div class="border-b border-purple-200 pb-4">
                          <h5 class="text-sm font-semibold text-gray-900 mb-3">Producer Information</h5>
                          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                            <div class="sm:col-span-2">
                              <label for="edit-producer-name" class="block text-xs font-medium text-gray-700">Producer Name</label>
                              <input
                                type="text"
                                id="edit-producer-name"
                                v-model="editForm.producer_name"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., Monastero di San Colombano"
                              />
                            </div>
                            <div>
                              <label for="edit-producer-type" class="block text-xs font-medium text-gray-700">Producer Type</label>
                              <select
                                id="edit-producer-type"
                                v-model="editForm.producer_type"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                              >
                                <option value="corporate">Corporate</option>
                                <option value="personal">Personal</option>
                              </select>
                            </div>
                            <div>
                              <label for="edit-producer-role" class="block text-xs font-medium text-gray-700">Producer Role</label>
                              <input
                                type="text"
                                id="edit-producer-role"
                                v-model="editForm.producer_role"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., producer, author"
                              />
                            </div>
                          </div>
                        </div>

                        <!-- Creator Information -->
                        <div class="border-b border-purple-200 pb-4">
                          <h5 class="text-sm font-semibold text-gray-900 mb-3">Creator Information</h5>
                          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                            <div class="sm:col-span-2">
                              <label for="edit-creator-name" class="block text-xs font-medium text-gray-700">Creator Name</label>
                              <input
                                type="text"
                                id="edit-creator-name"
                                v-model="editForm.creator_name"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., Giovanni Rossi"
                              />
                            </div>
                            <div>
                              <label for="edit-creator-type" class="block text-xs font-medium text-gray-700">Creator Type</label>
                              <select
                                id="edit-creator-type"
                                v-model="editForm.creator_type"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                              >
                                <option value="personal">Personal</option>
                                <option value="corporate">Corporate</option>
                              </select>
                            </div>
                            <div>
                              <label for="edit-creator-role" class="block text-xs font-medium text-gray-700">Creator Role</label>
                              <input
                                type="text"
                                id="edit-creator-role"
                                v-model="editForm.creator_role"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., creator, contributor"
                              />
                            </div>
                          </div>
                        </div>

                        <!-- Rights Metadata -->
                        <div class="border-b border-purple-200 pb-4">
                          <h5 class="text-sm font-semibold text-gray-900 mb-3">Rights Metadata</h5>
                          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                            <div>
                              <label for="edit-rights-category" class="block text-xs font-medium text-gray-700">Rights Category</label>
                              <select
                                id="edit-rights-category"
                                v-model="editForm.rights_category"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                              >
                                <option value="">Select category</option>
                                <option value="COPYRIGHTED">COPYRIGHTED</option>
                                <option value="PUBLIC DOMAIN">PUBLIC DOMAIN</option>
                                <option value="CONTRACTUAL">CONTRACTUAL</option>
                                <option value="OTHER">OTHER</option>
                              </select>
                            </div>
                            <div>
                              <label for="edit-rights-holder" class="block text-xs font-medium text-gray-700">Rights Holder</label>
                              <input
                                type="text"
                                id="edit-rights-holder"
                                v-model="editForm.rights_holder"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., Archivio di Stato"
                              />
                            </div>
                            <div>
                              <label for="edit-rights-constraint" class="block text-xs font-medium text-gray-700">Rights Constraint</label>
                              <input
                                type="text"
                                id="edit-rights-constraint"
                                v-model="editForm.rights_constraint"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., NoC-OKLR, InC"
                              />
                            </div>
                            <div>
                              <label for="edit-license-url" class="block text-xs font-medium text-gray-700">License URL</label>
                              <input
                                type="url"
                                id="edit-license-url"
                                v-model="editForm.license_url"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="https://..."
                              />
                            </div>
                            <div class="sm:col-span-2">
                              <label for="edit-rights-statement" class="block text-xs font-medium text-gray-700">Rights Statement</label>
                              <textarea
                                id="edit-rights-statement"
                                v-model="editForm.rights_statement"
                                rows="2"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="Additional rights information"
                              ></textarea>
                            </div>
                          </div>
                        </div>

                        <!-- Technical Metadata -->
                        <div class="border-b border-purple-200 pb-4">
                          <h5 class="text-sm font-semibold text-gray-900 mb-3">Technical Metadata</h5>
                          <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
                            <div>
                              <label for="edit-image-producer" class="block text-xs font-medium text-gray-700">Image Producer</label>
                              <input
                                type="text"
                                id="edit-image-producer"
                                v-model="editForm.image_producer"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., EDS Gamma"
                              />
                            </div>
                            <div>
                              <label for="edit-scanner-manufacturer" class="block text-xs font-medium text-gray-700">Scanner Manufacturer</label>
                              <input
                                type="text"
                                id="edit-scanner-manufacturer"
                                v-model="editForm.scanner_manufacturer"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., Metis Systems"
                              />
                            </div>
                            <div>
                              <label for="edit-scanner-model" class="block text-xs font-medium text-gray-700">Scanner Model</label>
                              <input
                                type="text"
                                id="edit-scanner-model"
                                v-model="editForm.scanner_model"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                                placeholder="e.g., DRS Scanner X"
                              />
                            </div>
                          </div>
                        </div>

                        <!-- Record Status -->
                        <div>
                          <label for="edit-record-status" class="block text-xs font-medium text-gray-700">Record Status</label>
                          <select
                            id="edit-record-status"
                            v-model="editForm.record_status"
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                          >
                            <option value="COMPLETE">COMPLETE</option>
                            <option value="MINIMUM">MINIMUM</option>
                            <option value="REFERENCED">REFERENCED</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Files Section -->
                  <div class="mt-8">
                    <h4 class="text-lg font-medium text-gray-900 mb-4">
                      Associated Files ({{ document?.document_files?.length || 0 }})
                    </h4>
                    
                    <div v-if="document?.document_files && document.document_files.length > 0" class="space-y-2">
                      <div
                        v-for="file in document.document_files"
                        :key="file.file_id"
                        @click="selectFile(file)"
                        :class="[
                          'p-3 rounded-lg border cursor-pointer transition-colors',
                          selectedFile && selectedFile.file_id === file.file_id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        ]"
                      >
                        <div class="flex items-center justify-between">
                          <div class="flex-1 min-w-0">
                            <p class="text-sm font-medium text-gray-900 truncate">{{ file.filename }}</p>
                            <div class="flex items-center space-x-4 text-xs text-gray-500">
                              <span>{{ formatFileSize(file.file_size) }}</span>
                              <span>{{ file.content_type }}</span>
                            </div>
                          </div>
                          <div class="flex items-center space-x-2">
                            <button
                              @click.stop="downloadFile(file)"
                              class="text-blue-600 hover:text-blue-800"
                              title="Download file"
                            >
                              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                              </svg>
                            </button>
                            <button
                              v-if="isEditing"
                              @click.stop="deleteFile(file)"
                              :disabled="deletingFileId === file.file_id"
                              class="text-red-600 hover:text-red-800 disabled:opacity-50"
                              title="Delete file"
                            >
                              <svg v-if="deletingFileId === file.file_id" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                              </svg>
                            </button>
                            </div>
                        </div>
                      </div>
                    </div>
                    
                    <div v-else class="text-center py-8">
                      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <p class="mt-2 text-sm text-gray-500">No files associated with this document</p>
                    </div>
                  </div>
                </div>

                <!-- Archive Tab -->
                <div v-if="activeTab === 'archive'" class="p-8">
                  <div class="space-y-6">
                    <!-- Archive Details -->
                    <div class="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200">
                      <div class="flex items-center gap-2 mb-4">
                        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                        </svg>
                        <h4 class="text-lg font-bold text-gray-900">Archive Details</h4>
                      </div>
                      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div v-if="document?.archive_name">
                          <dt class="text-sm font-medium text-blue-700">Archive Name</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.archive_name }}</dd>
                        </div>
                        <div v-if="document?.archive_contact">
                          <dt class="text-sm font-medium text-blue-700">Contact</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.archive_contact }}</dd>
                        </div>
                      </div>
                      <div v-if="!document?.archive_name && !document?.archive_contact" class="text-sm text-blue-600">
                        No archive details available
                      </div>
                    </div>

                    <!-- Archival Hierarchy -->
                    <div class="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200">
                      <div class="flex items-center gap-2 mb-4">
                        <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                        </svg>
                        <h4 class="text-lg font-bold text-gray-900">Archival Hierarchy</h4>
                      </div>
                      <div class="grid grid-cols-1 gap-4">
                        <div v-if="document?.fund_name">
                          <dt class="text-sm font-medium text-purple-700">Fund/Collection</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.fund_name }}</dd>
                        </div>
                        <div v-if="document?.series_name">
                          <dt class="text-sm font-medium text-purple-700">Series</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.series_name }}</dd>
                        </div>
                        <div v-if="document?.folder_number">
                          <dt class="text-sm font-medium text-purple-700">Folder/Unit Number</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.folder_number }}</dd>
                        </div>
                      </div>
                      <div v-if="!document?.fund_name && !document?.series_name && !document?.folder_number" class="text-sm text-purple-600">
                        No hierarchy information available
                      </div>
                    </div>

                    <!-- Temporal Information -->
                    <div class="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border border-green-200">
                      <div class="flex items-center gap-2 mb-4">
                        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <h4 class="text-lg font-bold text-gray-900">Temporal Information</h4>
                      </div>
                      <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
                        <div v-if="document?.date_from">
                          <dt class="text-sm font-medium text-green-700">Date From</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.date_from }}</dd>
                        </div>
                        <div v-if="document?.date_to">
                          <dt class="text-sm font-medium text-green-700">Date To</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.date_to }}</dd>
                        </div>
                        <div v-if="document?.period">
                          <dt class="text-sm font-medium text-green-700">Historical Period</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.period }}</dd>
                        </div>
                      </div>
                      <div v-if="!document?.date_from && !document?.date_to && !document?.period" class="text-sm text-green-600">
                        No temporal information available
                      </div>
                    </div>

                    <!-- Geographic & Contextual Information -->
                    <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 p-6 rounded-xl border border-yellow-200">
                      <div class="flex items-center gap-2 mb-4">
                        <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        <h4 class="text-lg font-bold text-gray-900">Geographic & Contextual</h4>
                      </div>
                      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div v-if="document?.location">
                          <dt class="text-sm font-medium text-yellow-700">Location</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.location }}</dd>
                        </div>
                        <div v-if="document?.language">
                          <dt class="text-sm font-medium text-yellow-700">Language</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.language }}</dd>
                        </div>
                        <div v-if="document?.subjects" class="md:col-span-2">
                          <dt class="text-sm font-medium text-yellow-700">Subjects/Keywords</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.subjects }}</dd>
                        </div>
                      </div>
                      <div v-if="!document?.location && !document?.language && !document?.subjects" class="text-sm text-yellow-600">
                        No geographic or contextual information available
                      </div>
                    </div>

                    <!-- Producer & Creator Information -->
                    <div class="bg-gradient-to-br from-indigo-50 to-indigo-100 p-6 rounded-xl border border-indigo-200">
                      <div class="flex items-center gap-2 mb-4">
                        <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        <h4 class="text-lg font-bold text-gray-900">Producer & Creator</h4>
                      </div>
                      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div v-if="document?.producer_name">
                          <dt class="text-sm font-medium text-indigo-700">Producer</dt>
                          <dd class="mt-1 text-base text-gray-900">
                            {{ document.producer_name }}
                            <span v-if="document.producer_type" class="text-sm text-gray-600">({{ document.producer_type }})</span>
                            <span v-if="document.producer_role" class="text-xs text-gray-500 block">{{ document.producer_role }}</span>
                          </dd>
                        </div>
                        <div v-if="document?.creator_name">
                          <dt class="text-sm font-medium text-indigo-700">Creator</dt>
                          <dd class="mt-1 text-base text-gray-900">
                            {{ document.creator_name }}
                            <span v-if="document.creator_type" class="text-sm text-gray-600">({{ document.creator_type }})</span>
                            <span v-if="document.creator_role" class="text-xs text-gray-500 block">{{ document.creator_role }}</span>
                          </dd>
                        </div>
                      </div>
                      <div v-if="!document?.producer_name && !document?.creator_name" class="text-sm text-indigo-600">
                        No producer or creator information available
                      </div>
                    </div>

                    <!-- Rights Information -->
                    <div class="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-xl border border-red-200">
                      <div class="flex items-center gap-2 mb-4">
                        <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                        <h4 class="text-lg font-bold text-gray-900">Rights & Licensing</h4>
                      </div>
                      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div v-if="document?.rights_category">
                          <dt class="text-sm font-medium text-red-700">Rights Category</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.rights_category }}</dd>
                        </div>
                        <div v-if="document?.rights_holder">
                          <dt class="text-sm font-medium text-red-700">Rights Holder</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.rights_holder }}</dd>
                        </div>
                        <div v-if="document?.rights_constraint">
                          <dt class="text-sm font-medium text-red-700">Rights Constraint</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.rights_constraint }}</dd>
                        </div>
                        <div v-if="document?.license_url">
                          <dt class="text-sm font-medium text-red-700">License URL</dt>
                          <dd class="mt-1 text-base text-gray-900">
                            <a :href="document.license_url" target="_blank" class="text-blue-600 hover:underline">{{ document.license_url }}</a>
                          </dd>
                        </div>
                        <div v-if="document?.rights_statement" class="md:col-span-2">
                          <dt class="text-sm font-medium text-red-700">Rights Statement</dt>
                          <dd class="mt-1 text-base text-gray-900">{{ document.rights_statement }}</dd>
                        </div>
                      </div>
                      <div v-if="!document?.rights_category && !document?.rights_holder && !document?.license_url" class="text-sm text-red-600">
                        No rights information available
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Files Tab -->
                <div v-if="activeTab === 'files'" class="p-8">
                  <div v-if="document?.document_files && document.document_files.length > 0">
                    <!-- Files Grid -->
                    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                      <div
                        v-for="file in document.document_files"
                        :key="file.file_id"
                        class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden hover:border-blue-400 transition-all duration-200 hover:shadow-lg"
                      >
                        <!-- Image Preview -->
                        <div
                          class="relative bg-gray-100 aspect-square overflow-hidden cursor-pointer group"
                          @click="selectFile(file)"
                        >
                          <!-- DNG Badge -->
                          <div v-if="isDNGFile(file)" class="absolute top-2 left-2 z-10 bg-blue-600 text-white px-2 py-1 rounded-full text-xs font-semibold shadow-lg flex items-center space-x-1">
                            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"/>
                            </svg>
                            <span>DNG RAW</span>
                          </div>

                          <img
                            v-if="isImageFile(file) && getFileThumbnail(file)"
                            :src="getFileThumbnail(file)"
                            :alt="file.filename"
                            class="w-full h-full object-cover group-hover:opacity-90 transition-opacity"
                          />
                          <div
                            v-else-if="isImageFile(file)"
                            class="w-full h-full flex items-center justify-center"
                          >
                            <svg class="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
                              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                          </div>
                          <div
                            v-else
                            class="w-full h-full flex items-center justify-center"
                          >
                            <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </div>

                          <!-- Hover overlay -->
                          <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                            <span class="text-white opacity-0 group-hover:opacity-100 font-medium">Click to view details</span>
                          </div>
                        </div>

                        <!-- File Info -->
                        <div class="p-4">
                          <h5 class="text-sm font-semibold text-gray-900 truncate mb-3" :title="file.filename">
                            {{ file.filename }}
                          </h5>

                          <!-- Camera Info - Prominently Displayed -->
                          <div v-if="file.scanner_manufacturer || file.scanner_model_name" class="mb-3 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                            <div class="flex items-center gap-1 mb-1">
                              <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M4 5a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V7a2 2 0 00-2-2h-1.586a1 1 0 01-.707-.293l-1.121-1.121A2 2 0 0011.172 3H8.828a2 2 0 00-1.414.586L6.293 4.707A1 1 0 015.586 5H4zm6 9a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                              </svg>
                              <span class="text-xs font-bold text-blue-900 uppercase tracking-wide">Camera</span>
                            </div>
                            <div v-if="file.scanner_manufacturer" class="text-sm font-bold text-gray-900 mb-0.5">
                              {{ file.scanner_manufacturer }}
                            </div>
                            <div v-if="file.scanner_model_name" class="text-sm font-medium text-gray-700">
                              {{ file.scanner_model_name }}
                            </div>
                          </div>

                          <!-- Technical Details -->
                          <div class="space-y-2 text-xs text-gray-600">
                            <div v-if="file.image_width && file.image_height" class="flex items-center gap-1">
                              <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                              </svg>
                              <span>{{ file.image_width }} × {{ file.image_height }} px</span>
                            </div>
                            <div class="flex items-center gap-1">
                              <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                              </svg>
                              <span>{{ formatFileSize(file.file_size) }}</span>
                            </div>
                            <div v-if="file.x_sampling_frequency" class="flex items-center gap-1">
                              <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 00-2-2m0 0h2a2 2 0 012 2v0a2 2 0 01-2 2h-2a2 2 0 01-2-2v0z" />
                              </svg>
                              <span>{{ file.x_sampling_frequency }} DPI</span>
                            </div>
                          </div>

                          <!-- Action Buttons -->
                          <div class="mt-4 flex gap-2">
                            <button
                              @click.stop="downloadFile(file)"
                              class="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 text-xs font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                              </svg>
                              Download
                            </button>
                            <button
                              v-if="isEditing"
                              @click.stop="deleteFile(file)"
                              :disabled="deletingFileId === file.file_id"
                              class="px-3 py-2 border border-red-300 text-xs font-medium rounded-lg text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
                            >
                              <svg v-if="deletingFileId === file.file_id" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- No Files Message -->
                  <div v-else class="text-center py-12">
                    <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <h3 class="mt-4 text-lg font-medium text-gray-900">No files uploaded</h3>
                    <p class="mt-2 text-sm text-gray-500">Upload files in edit mode to see them here</p>
                  </div>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- Image Detail Modal -->
  <TransitionRoot appear :show="!!selectedFile && showFileDetail" as="template">
    <Dialog as="div" class="relative z-[60]" :static="true">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-75" @click="closeFileDetail" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-6xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
              <!-- Header -->
              <div class="flex items-center justify-between p-6 border-b border-gray-200">
                <div class="flex-1">
                  <h3 class="text-xl font-bold text-gray-900">{{ selectedFile?.filename }}</h3>
                  <p class="mt-1 text-sm text-gray-600">File Details & Metadata</p>
                </div>
                <button
                  @click="closeFileDetail"
                  class="rounded-md bg-white text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Content -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 max-h-[70vh] overflow-y-auto">
                <!-- Left: Image Preview -->
                <div>
                  <div class="relative bg-gray-50 rounded-lg overflow-hidden" style="min-height: 300px;">
                    <!-- DNG File Badge -->
                    <div v-if="isDNGFile(selectedFile)" class="absolute top-2 left-2 z-10 bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg flex items-center space-x-1">
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"/>
                      </svg>
                      <span>DNG RAW</span>
                    </div>
                    <img
                      v-if="imageDataUrl && imageLoaded && !imageError"
                      :src="imageDataUrl"
                      :alt="selectedFile.filename"
                      @click="openImageViewer"
                      class="w-full h-auto cursor-pointer hover:opacity-90 transition-opacity"
                      :title="isDNGFile(selectedFile) ? 'DNG preview (auto-generated thumbnail) - Click to view' : 'Click to view full size'"
                    />

                    <div v-if="!imageLoaded && !imageError" class="absolute inset-0 flex items-center justify-center">
                      <div class="flex items-center space-x-2">
                        <svg class="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span class="text-gray-600">Loading preview...</span>
                      </div>
                    </div>

                    <div v-if="imageError" class="absolute inset-0 flex items-center justify-center">
                      <div class="text-center">
                        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        <p class="mt-2 text-sm text-gray-500">Preview not available</p>
                      </div>
                    </div>
                  </div>

                  <!-- DNG Preview Note -->
                  <div v-if="isDNGFile(selectedFile)" class="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-800">
                    <div class="flex items-start space-x-1">
                      <svg class="w-3 h-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                      <span>Preview auto-generated from DNG file. Download for full quality RAW image.</span>
                    </div>
                  </div>
                </div>

                <!-- Right: Metadata -->
                <div class="space-y-4">
                  <!-- Image Details - Basic Info -->
                  <div class="bg-gray-50 rounded-lg p-4">
                    <h5 class="text-sm font-medium text-gray-900 mb-2">Basic Information</h5>
                    <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                      <div>
                        <dt class="text-gray-500">File Size:</dt>
                        <dd class="text-gray-900">{{ formatFileSize(selectedFile.file_size) }}</dd>
                      </div>
                      <div>
                        <dt class="text-gray-500">Format:</dt>
                        <dd class="text-gray-900">{{ selectedFile.format_name || selectedFile.content_type }}</dd>
                      </div>
                      <div v-if="selectedFile.image_width && selectedFile.image_height" class="col-span-2">
                        <dt class="text-gray-500">Dimensions:</dt>
                        <dd class="text-gray-900">{{ selectedFile.image_width }} × {{ selectedFile.image_height }} pixels</dd>
                      </div>
                      <div v-if="selectedFile.checksum_md5" class="col-span-2">
                        <dt class="text-gray-500">MD5 Checksum:</dt>
                        <dd class="text-gray-900 font-mono text-xs break-all">{{ selectedFile.checksum_md5 }}</dd>
                      </div>
                    </dl>
                  </div>

                  <!-- Technical Metadata (MIX) -->
                  <div v-if="hasMetadata(selectedFile)" class="bg-gray-50 rounded-lg p-4">
                    <button
                      type="button"
                      @click.stop="showTechnicalMetadata = !showTechnicalMetadata"
                      class="w-full flex items-center justify-between text-sm font-medium text-gray-900 hover:text-gray-700"
                    >
                      <span>📊 Technical Metadata (METS MIX)</span>
                      <svg
                        :class="['w-4 h-4 transition-transform', showTechnicalMetadata ? 'rotate-180' : '']"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    <div v-if="showTechnicalMetadata" class="mt-3 pt-3 border-t border-gray-200">
                      <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                        <div v-if="selectedFile.color_space">
                          <dt class="text-gray-500">Color Space:</dt>
                          <dd class="text-gray-900">{{ selectedFile.color_space }}</dd>
                        </div>
                        <div v-if="selectedFile.bits_per_sample">
                          <dt class="text-gray-500">Bits per Sample:</dt>
                          <dd class="text-gray-900">{{ selectedFile.bits_per_sample }}</dd>
                        </div>
                        <div v-if="selectedFile.samples_per_pixel">
                          <dt class="text-gray-500">Samples per Pixel:</dt>
                          <dd class="text-gray-900">{{ selectedFile.samples_per_pixel }}</dd>
                        </div>
                        <div v-if="selectedFile.compression_scheme">
                          <dt class="text-gray-500">Compression:</dt>
                          <dd class="text-gray-900">{{ selectedFile.compression_scheme }}</dd>
                        </div>
                        <div v-if="selectedFile.x_sampling_frequency">
                          <dt class="text-gray-500">Resolution (DPI):</dt>
                          <dd class="text-gray-900">{{ selectedFile.x_sampling_frequency }} × {{ selectedFile.y_sampling_frequency || selectedFile.x_sampling_frequency }}</dd>
                        </div>
                        <div v-if="selectedFile.orientation">
                          <dt class="text-gray-500">Orientation:</dt>
                          <dd class="text-gray-900">{{ selectedFile.orientation }}</dd>
                        </div>
                        <div v-if="selectedFile.byte_order" class="col-span-2">
                          <dt class="text-gray-500">Byte Order:</dt>
                          <dd class="text-gray-900">{{ selectedFile.byte_order }}</dd>
                        </div>
                        <div v-if="selectedFile.icc_profile_name" class="col-span-2">
                          <dt class="text-gray-500">ICC Profile:</dt>
                          <dd class="text-gray-900">{{ selectedFile.icc_profile_name }}</dd>
                        </div>
                      </dl>
                    </div>
                  </div>

                  <!-- Camera/Scanner Metadata -->
                  <div v-if="hasCameraMetadata(selectedFile)" class="bg-gray-50 rounded-lg p-4">
                    <button
                      type="button"
                      @click.stop="showCameraMetadata = !showCameraMetadata"
                      class="w-full flex items-center justify-between text-sm font-medium text-gray-900 hover:text-gray-700"
                    >
                      <span>📷 Camera/Scanner Information</span>
                      <svg
                        :class="['w-4 h-4 transition-transform', showCameraMetadata ? 'rotate-180' : '']"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    <div v-if="showCameraMetadata" class="mt-3 pt-3 border-t border-gray-200">
                      <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                        <div v-if="selectedFile.scanner_manufacturer" class="col-span-2">
                          <dt class="text-gray-500">Camera/Scanner Manufacturer:</dt>
                          <dd class="text-gray-900">{{ selectedFile.scanner_manufacturer }}</dd>
                        </div>
                        <div v-if="selectedFile.scanner_model_name" class="col-span-2">
                          <dt class="text-gray-500">Camera/Scanner Model:</dt>
                          <dd class="text-gray-900">{{ selectedFile.scanner_model_name }}</dd>
                        </div>
                        <div v-if="selectedFile.scanning_software_name" class="col-span-2">
                          <dt class="text-gray-500">Software:</dt>
                          <dd class="text-gray-900">
                            {{ selectedFile.scanning_software_name }}
                            <span v-if="selectedFile.scanning_software_version"> v{{ selectedFile.scanning_software_version }}</span>
                          </dd>
                        </div>
                        <div v-if="selectedFile.date_time_created" class="col-span-2">
                          <dt class="text-gray-500">Date Captured:</dt>
                          <dd class="text-gray-900">{{ formatDate(selectedFile.date_time_created) }}</dd>
                        </div>
                      </dl>
                    </div>
                  </div>

                  <!-- Complete DNG/RAW Metadata -->
                  <div v-if="selectedFile.raw_metadata && Object.keys(selectedFile.raw_metadata).length > 0" class="bg-gray-50 rounded-lg p-4">
                    <button
                      type="button"
                      @click.stop="showRawMetadata = !showRawMetadata"
                      class="w-full flex items-center justify-between text-sm font-medium text-gray-900 hover:text-gray-700"
                    >
                      <span>🔬 Complete DNG/EXIF Metadata ({{ Object.keys(selectedFile.raw_metadata).length }} fields)</span>
                      <svg
                        :class="['w-4 h-4 transition-transform', showRawMetadata ? 'rotate-180' : '']"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    <div v-if="showRawMetadata" class="mt-3 pt-3 border-t border-gray-200">
                      <div class="max-h-96 overflow-y-auto">
                        <dl class="space-y-2 text-xs">
                          <div
                            v-for="(value, key) in selectedFile.raw_metadata"
                            :key="key"
                            class="grid grid-cols-5 gap-2 py-1 border-b border-gray-200 last:border-0"
                          >
                            <dt class="col-span-2 text-gray-500 font-mono text-xs break-all">{{ key }}:</dt>
                            <dd class="col-span-3 text-gray-900 font-mono text-xs break-all">
                              {{ formatMetadataValue(value) }}
                            </dd>
                          </div>
                        </dl>
                      </div>

                      <!-- Export Button -->
                      <div class="mt-3 pt-3 border-t border-gray-200">
                        <button
                          @click="downloadMetadataJSON"
                          class="w-full inline-flex items-center justify-center px-3 py-2 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                        >
                          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                          </svg>
                          Download as JSON
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- Simple Image Viewer Modal -->
  <TransitionRoot appear :show="showImageViewer" as="template">
    <Dialog as="div" @close="closeImageViewer" class="relative z-[70]">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-90" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="relative max-w-7xl max-h-[90vh] transform overflow-hidden rounded-lg bg-white p-4">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium text-gray-900">{{ selectedFile?.filename }}</h3>
                <button
                  @click="closeImageViewer"
                  class="rounded-md bg-white text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div class="flex justify-center">
                <img
                  v-if="imageDataUrl"
                  :src="imageDataUrl"
                  :alt="selectedFile?.filename"
                  class="max-w-full max-h-[80vh] object-contain"
                />
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import axios from 'axios'

export default {
  name: 'DocumentDetailModal',
  components: {
    Dialog,
    DialogPanel,
    DialogTitle,
    TransitionChild,
    TransitionRoot,
  },
  props: {
    document: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'documentUpdated', 'documentDeleted'],
  setup(props, { emit }) {
    const authStore = useAuthStore()

    // State
    const isEditing = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const selectedFile = ref(null)
    const deletingFileId = ref(null)
    const imageDataUrl = ref('')
    const imageLoaded = ref(false)
    const imageError = ref(false)
    const showImageViewer = ref(false)
    const showFileDetail = ref(false)
    const selectedImageFile = ref(null)
    const imageUploading = ref(false)
    const imageUploadProgress = ref(0)
    const isImageDragOver = ref(false)
    const imageInput = ref(null)

    // Metadata display state
    const showTechnicalMetadata = ref(false)
    const showCameraMetadata = ref(false)
    const showRawMetadata = ref(false)

    // Tab state
    const activeTab = ref('overview') // 'overview', 'archive', 'files'

    // Image blob URLs for Files tab (file_id -> blob URL)
    const imageBlobUrls = ref({})

    // Edit form
    const editForm = reactive({
      // Basic Information
      logical_id: '',
      conservative_id: '',
      conservative_id_authority: '',
      title: '',
      description: '',
      document_type: '',
      total_pages: null,

      // Archive Information
      archive_name: '',
      archive_contact: '',
      fund_name: '',
      series_name: '',
      folder_number: '',

      // Temporal & Contextual Information
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

    // Computed
    const imageFiles = computed(() => {
      return props.document?.document_files?.filter(file => isImageFile(file)) || []
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

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
    }

    const isImageFile = (file) => {
      return file && file.content_type && file.content_type.startsWith('image/')
    }

    const isDNGFile = (file) => {
      if (!file) return false
      const dngMimeTypes = ['image/x-adobe-dng', 'image/dng', 'image/x-dng']
      if (file.content_type && dngMimeTypes.includes(file.content_type)) return true
      if (file.filename && file.filename.toLowerCase().endsWith('.dng')) return true
      return false
    }

    const hasMetadata = (file) => {
      if (!file) return false
      return !!(
        file.color_space ||
        file.bits_per_sample ||
        file.samples_per_pixel ||
        file.compression_scheme ||
        file.x_sampling_frequency ||
        file.orientation ||
        file.byte_order ||
        file.icc_profile_name
      )
    }

    const hasCameraMetadata = (file) => {
      if (!file) return false
      return !!(
        file.scanner_manufacturer ||
        file.scanner_model_name ||
        file.scanning_software_name ||
        file.date_time_created
      )
    }

    const formatMetadataValue = (value) => {
      if (value === null || value === undefined) return 'N/A'
      if (Array.isArray(value)) {
        return `[${value.join(', ')}]`
      }
      if (typeof value === 'object') {
        return JSON.stringify(value)
      }
      return String(value)
    }

    const downloadMetadataJSON = () => {
      if (!selectedFile.value || !selectedFile.value.raw_metadata) return

      const metadata = {
        filename: selectedFile.value.filename,
        extracted_metadata: selectedFile.value.raw_metadata,
        technical_fields: {
          image_width: selectedFile.value.image_width,
          image_height: selectedFile.value.image_height,
          color_space: selectedFile.value.color_space,
          bits_per_sample: selectedFile.value.bits_per_sample,
          samples_per_pixel: selectedFile.value.samples_per_pixel,
          compression_scheme: selectedFile.value.compression_scheme,
          x_sampling_frequency: selectedFile.value.x_sampling_frequency,
          y_sampling_frequency: selectedFile.value.y_sampling_frequency,
          orientation: selectedFile.value.orientation,
          icc_profile_name: selectedFile.value.icc_profile_name,
          scanner_manufacturer: selectedFile.value.scanner_manufacturer,
          scanner_model_name: selectedFile.value.scanner_model_name,
          scanning_software_name: selectedFile.value.scanning_software_name
        }
      }

      const blob = new Blob([JSON.stringify(metadata, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${selectedFile.value.filename}_metadata.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    const selectFile = async (file) => {
      // Don't open file detail modal when in edit mode
      if (isEditing.value) {
        return
      }

      selectedFile.value = file
      showFileDetail.value = true

      if (isImageFile(file)) {
        await loadImagePreview(file)
      }
    }

    const loadImagePreview = async (file) => {
      imageLoaded.value = false
      imageError.value = false
      imageDataUrl.value = ''

      try {
        const url = `${import.meta.env.VITE_API_URL}/api/files/${file.file_id}/stream`

        const response = await axios.get(url, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          },
          responseType: 'blob'
        })

        const blob = new Blob([response.data], { type: file.content_type })
        const imageUrl = URL.createObjectURL(blob)

        const img = new Image()
        img.onload = () => {
          imageDataUrl.value = imageUrl
          imageLoaded.value = true
        }
        img.onerror = () => {
          imageError.value = true
          URL.revokeObjectURL(imageUrl)
        }
        img.src = imageUrl

      } catch (err) {
        console.error('Error loading image:', err)
        imageError.value = true
      }
    }

    const downloadFile = async (file) => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/files/${file.file_id}/stream`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            },
            responseType: 'blob'
          }
        )

        const blob = new Blob([response.data], { type: file.content_type })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = file.filename
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error downloading file:', err)
        alert('Failed to download file: ' + (err.response?.data?.detail || err.message))
      }
    }

    const deleteFile = async (file) => {
      if (!confirm(`Are you sure you want to delete "${file.filename}"? This action cannot be undone.`)) {
        return
      }

      deletingFileId.value = file.file_id

      try {
        await axios.delete(
          `${import.meta.env.VITE_API_URL}/api/documents/${props.document.id}/files/${file.file_id}`,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          }
        )

        // Remove file from document
        const updatedDocument = { ...props.document }
        updatedDocument.document_files = updatedDocument.document_files.filter(f => f.file_id !== file.file_id)

        // Clear selection if deleted file was selected
        if (selectedFile.value && selectedFile.value.file_id === file.file_id) {
          selectedFile.value = null
          imageDataUrl.value = ''
          imageLoaded.value = false
          imageError.value = false
          showFileDetail.value = false
        }

        emit('documentUpdated', updatedDocument)

      } catch (err) {
        console.error('Error deleting file:', err)
        alert('Failed to delete file: ' + (err.response?.data?.detail || err.message))
      } finally {
        deletingFileId.value = null
      }
    }

    // Image viewer methods
    const openImageViewer = () => {
      if (imageDataUrl.value && imageLoaded.value) {
        showImageViewer.value = true
      }
    }

    const closeImageViewer = () => {
      showImageViewer.value = false
    }

    // Edit methods
    const startEdit = () => {
      // Close any open file detail modal
      showFileDetail.value = false
      selectedFile.value = null

      // Switch to Overview tab for editing
      activeTab.value = 'overview'

      // Basic Information
      editForm.logical_id = props.document.logical_id || ''
      editForm.conservative_id = props.document.conservative_id || ''
      editForm.conservative_id_authority = props.document.conservative_id_authority || ''
      editForm.title = props.document.title || ''
      editForm.description = props.document.description || ''
      editForm.document_type = props.document.document_type || ''
      editForm.total_pages = props.document.total_pages || null

      // Archive Information
      editForm.archive_name = props.document.archive_name || ''
      editForm.archive_contact = props.document.archive_contact || ''
      editForm.fund_name = props.document.fund_name || ''
      editForm.series_name = props.document.series_name || ''
      editForm.folder_number = props.document.folder_number || ''

      // Temporal & Contextual Information
      editForm.date_from = props.document.date_from || ''
      editForm.date_to = props.document.date_to || ''
      editForm.period = props.document.period || ''
      editForm.location = props.document.location || ''
      editForm.language = props.document.language || ''
      editForm.subjects = props.document.subjects || ''

      isEditing.value = true
    }

    const cancelEdit = () => {
      isEditing.value = false
      Object.keys(editForm).forEach(key => {
        editForm[key] = ''
      })
    }

    const saveChanges = async () => {
      saving.value = true

      try {
        const response = await axios.put(
          `${import.meta.env.VITE_API_URL}/api/documents/${props.document.id}`,
          editForm,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'application/json'
            }
          }
        )

        // Update the local document data immediately to reflect changes
        Object.assign(props.document, response.data)

        emit('documentUpdated', response.data)
        isEditing.value = false

        // Show success feedback
        console.log('Document updated successfully')

      } catch (err) {
        console.error('Error updating document:', err)
        alert('Failed to update document: ' + (err.response?.data?.detail || err.message))
      } finally {
        saving.value = false
      }
    }

    const deleteDocument = async () => {
      if (!confirm(`Are you sure you want to delete this document? This action cannot be undone.`)) {
        return
      }

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

        emit('documentDeleted', props.document.id)
        closeModal()

      } catch (err) {
        console.error('Error deleting document:', err)
        alert('Failed to delete document: ' + (err.response?.data?.detail || err.message))
      } finally {
        deleting.value = false
      }
    }

    // Image upload methods
    const triggerImageInput = () => {
      imageInput.value?.click()
    }

    const handleImageSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        validateAndSetImage(file)
      }
    }

    const handleImageDrop = (event) => {
      event.preventDefault()
      isImageDragOver.value = false
      const file = event.dataTransfer.files[0]
      if (file) {
        validateAndSetImage(file)
      }
    }

    const validateAndSetImage = async (file) => {
      // Check file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff']
      if (!allowedTypes.includes(file.type)) {
        alert('Please select a valid image file (JPEG, PNG, or TIFF)')
        return
      }

      // Check file size (20MB limit)
      if (file.size > 20 * 1024 * 1024) {
        alert('Image file must be smaller than 20MB')
        return
      }

      selectedImageFile.value = file

      // Automatically upload the image
      await uploadImage()
    }

    const clearSelectedImage = () => {
      selectedImageFile.value = null
      if (imageInput.value) {
        imageInput.value.value = ''
      }
    }

    const uploadImage = async () => {
      if (!selectedImageFile.value) return

      imageUploading.value = true
      imageUploadProgress.value = 0

      try {
        const formData = new FormData()
        formData.append('file', selectedImageFile.value)
        formData.append('logical_id', props.document.logical_id)

        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/files/upload-image`,
          formData,
          {
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              imageUploadProgress.value = progress
            }
          }
        )

        // Clear the selection and refresh the document
        clearSelectedImage()
        emit('documentUpdated', response.data.document)
        alert('Image uploaded successfully!')

      } catch (err) {
        console.error('Error uploading image:', err)
        alert('Failed to upload image: ' + (err.response?.data?.detail || err.message))
      } finally {
        imageUploading.value = false
        imageUploadProgress.value = 0
      }
    }

    const getImageUrl = (file) => {
      if (!file || !file.file_id) return ''
      return `${import.meta.env.VITE_API_URL}/api/files/${file.file_id}/stream`
    }

    const handleImageError = (event) => {
      // Hide broken image and show placeholder
      event.target.style.display = 'none'
    }

    // Load all images as blob URLs for the Files tab
    const loadAllImagePreviews = async () => {
      if (!props.document?.document_files) return

      for (const file of props.document.document_files) {
        if (isImageFile(file) && !imageBlobUrls.value[file.file_id]) {
          try {
            const response = await axios.get(
              `${import.meta.env.VITE_API_URL}/api/files/${file.file_id}/stream`,
              {
                headers: {
                  'Authorization': `Bearer ${authStore.token}`
                },
                responseType: 'blob'
              }
            )

            const blob = new Blob([response.data], { type: file.content_type })
            const blobUrl = URL.createObjectURL(blob)
            imageBlobUrls.value[file.file_id] = blobUrl
          } catch (err) {
            console.error(`Error loading image ${file.file_id}:`, err)
          }
        }
      }
    }

    // Get image URL - returns blob URL if available, otherwise placeholder
    const getFileThumbnail = (file) => {
      return imageBlobUrls.value[file.file_id] || ''
    }

    // Watchers
    watch(() => props.document, (newDoc) => {
      if (newDoc && newDoc.document_files && newDoc.document_files.length > 0) {
        // Load image previews when document is opened
        loadAllImagePreviews()
      } else {
        selectedFile.value = null
        imageDataUrl.value = ''
        imageLoaded.value = false
        imageError.value = false
        imageBlobUrls.value = {}
      }
    }, { immediate: true })

    // Watch for tab changes to load images when Files tab is opened
    watch(activeTab, (newTab) => {
      if (newTab === 'files' && props.document?.document_files) {
        loadAllImagePreviews()
      }
    })

    // Lifecycle
    onMounted(() => {
      // Don't auto-select on mount anymore
    })

    return {
      // State
      isEditing,
      saving,
      deleting,
      selectedFile,
      deletingFileId,
      imageDataUrl,
      imageLoaded,
      imageError,
      showImageViewer,
      showFileDetail,
      selectedImageFile,
      imageUploading,
      imageUploadProgress,
      isImageDragOver,
      imageInput,
      editForm,

      // Metadata display state
      showTechnicalMetadata,
      showCameraMetadata,
      showRawMetadata,

      // Tab state
      activeTab,
      imageBlobUrls,

      // Computed
      imageFiles,

      // Methods
      closeModal,
      closeFileDetail,
      formatDate,
      formatFileSize,
      isImageFile,
      isDNGFile,
      hasMetadata,
      hasCameraMetadata,
      formatMetadataValue,
      downloadMetadataJSON,
      getImageUrl,
      handleImageError,
      loadAllImagePreviews,
      getFileThumbnail,
      selectFile,
      downloadFile,
      deleteFile,
      openImageViewer,
      closeImageViewer,
      startEdit,
      cancelEdit,
      saveChanges,
      deleteDocument,
      triggerImageInput,
      handleImageSelect,
      handleImageDrop,
      clearSelectedImage,
      uploadImage
    }
  }
}
</script>
