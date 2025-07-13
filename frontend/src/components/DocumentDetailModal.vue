<template>
  <!-- Document Detail Modal -->
  <TransitionRoot appear :show="!!document" as="template">
    <Dialog as="div" @close="closeModal" class="relative z-50">
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
              <div class="flex items-center justify-between p-6 border-b border-gray-200">
                <div>
                  <DialogTitle as="h3" class="text-xl font-semibold leading-6 text-gray-900">
                    {{ document?.title || document?.logical_id || 'Document Details' }}
                  </DialogTitle>
                  <p class="mt-1 text-sm text-gray-500">
                    Logical ID: {{ document?.logical_id }}
                  </p>
                </div>
                <div class="flex items-center space-x-3">
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

              <!-- Content -->
              <div class="flex h-[600px]">
                <!-- Left Panel - Metadata -->
                <div class="w-1/2 p-6 border-r border-gray-200 overflow-y-auto">
                  <h4 class="text-lg font-medium text-gray-900 mb-4">Document Metadata</h4>
                  
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

                <!-- Right Panel - Image Preview -->
                <div class="w-1/2 p-6 overflow-y-auto">
                  <div v-if="selectedFile">
                    <h4 class="text-lg font-medium text-gray-900 mb-4">File Preview</h4>
                    <p class="text-sm text-gray-500 mb-4">{{ selectedFile.filename }}</p>
                    
                    <!-- Image Preview -->
                    <div v-if="isImageFile(selectedFile)" class="space-y-4">
                      <div class="relative bg-gray-50 rounded-lg overflow-hidden" style="min-height: 300px;">
                        <img
                          v-if="imageDataUrl && imageLoaded && !imageError"
                          :src="imageDataUrl"
                          :alt="selectedFile.filename"
                          @click="openImageViewer"
                          class="w-full h-auto cursor-pointer hover:opacity-90 transition-opacity"
                          title="Click to view full size"
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
                      
                      <!-- Image Details -->
                      <div class="bg-gray-50 rounded-lg p-4">
                        <h5 class="text-sm font-medium text-gray-900 mb-2">Image Details</h5>
                        <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                          <div>
                            <dt class="text-gray-500">Size:</dt>
                            <dd class="text-gray-900">{{ formatFileSize(selectedFile.file_size) }}</dd>
                          </div>
                          <div>
                            <dt class="text-gray-500">Type:</dt>
                            <dd class="text-gray-900">{{ selectedFile.content_type }}</dd>
                          </div>
                          <div v-if="selectedFile.image_width && selectedFile.image_height" class="col-span-2">
                            <dt class="text-gray-500">Dimensions:</dt>
                            <dd class="text-gray-900">{{ selectedFile.image_width }} × {{ selectedFile.image_height }} pixels</dd>
                          </div>
                          <div v-if="selectedFile.checksum_md5" class="col-span-2">
                            <dt class="text-gray-500">MD5:</dt>
                            <dd class="text-gray-900 font-mono text-xs break-all">{{ selectedFile.checksum_md5 }}</dd>
                          </div>
                        </dl>
                      </div>
                    </div>
                    
                    <!-- Non-Image File Preview -->
                    <div v-else class="text-center py-12">
                      <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <h5 class="mt-4 text-lg font-medium text-gray-900">{{ selectedFile.filename }}</h5>
                      <div class="mt-4 bg-gray-50 rounded-lg p-4">
                        <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                          <div>
                            <dt class="text-gray-500">Type:</dt>
                            <dd class="text-gray-900">{{ selectedFile.content_type }}</dd>
                          </div>
                          <div>
                            <dt class="text-gray-500">Size:</dt>
                            <dd class="text-gray-900">{{ formatFileSize(selectedFile.file_size) }}</dd>
                          </div>
                          <div v-if="selectedFile.checksum_md5" class="col-span-2">
                            <dt class="text-gray-500">MD5:</dt>
                            <dd class="text-gray-900 font-mono text-xs break-all">{{ selectedFile.checksum_md5 }}</dd>
                          </div>
                        </dl>
                      </div>
                    </div>
                  </div>
                  
                  <!-- No File Selected -->
                  <div v-else class="text-center py-12">
                    <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    <p class="mt-4 text-lg font-medium text-gray-900">No file selected</p>
                    <p class="mt-2 text-sm text-gray-500">Select a file from the list to preview it</p>
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
    <Dialog as="div" @close="closeImageViewer" class="relative z-[60]">
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
            <DialogPanel class="relative max-w-4xl max-h-[90vh] transform overflow-hidden rounded-lg bg-white p-4">
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
                  class="max-w-full max-h-[70vh] object-contain"
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
    const selectedImageFile = ref(null)
    const imageUploading = ref(false)
    const imageUploadProgress = ref(0)
    const isImageDragOver = ref(false)
    const imageInput = ref(null)
    
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
      subjects: ''
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

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      try {
        return new Date(dateString).toLocaleDateString()
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

    const selectFile = async (file) => {
      selectedFile.value = file
      
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
      
      // Load the first image if available
      if (imageFiles.value.length > 0) {
        selectFile(imageFiles.value[0])
      }
      
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

    // Watchers
    watch(() => props.document, (newDoc) => {
      if (newDoc && newDoc.document_files && newDoc.document_files.length > 0) {
        selectFile(newDoc.document_files[0])
      } else {
        selectedFile.value = null
        imageDataUrl.value = ''
        imageLoaded.value = false
        imageError.value = false
      }
    }, { immediate: true })

    // Lifecycle
    onMounted(() => {
      if (props.document?.document_files && props.document.document_files.length > 0) {
        selectFile(props.document.document_files[0])
      }
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
      selectedImageFile,
      imageUploading,
      imageUploadProgress,
      isImageDragOver,
      imageInput,
      editForm,
      
      // Computed
      imageFiles,
      
      // Methods
      closeModal,
      formatDate,
      formatFileSize,
      isImageFile,
      getImageUrl,
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