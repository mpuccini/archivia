<template>
  <div class="space-y-6">
    <!-- Header with actions -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Document Management</h2>
        <p class="mt-1 text-sm text-gray-600">Manage and organize your digital archives</p>
      </div>
      <div class="mt-4 sm:mt-0 sm:flex sm:space-x-3">
        <button
          @click="showUploadForm = true"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          New Document
        </button>
        
        <!-- Batch Operations Dropdown -->
        <Menu as="div" class="relative inline-block text-left">
          <div>
            <MenuButton class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
              </svg>
              Batch Operations
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </MenuButton>
          </div>

          <transition
            enter-active-class="transition duration-100 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
          >
            <MenuItems class="absolute right-0 z-50 mt-2 w-56 origin-top-right bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
              <div class="py-1">
                <MenuItem v-slot="{ active }">
                  <button
                    @click="showExcelBatchImport = true"
                    :class="[
                      active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                      'group flex items-center px-4 py-2 text-sm w-full text-left'
                    ]"
                  >
                    <svg class="mr-3 h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a4 4 0 01-4-4V5a4 4 0 014-4h6l4 4v10a4 4 0 01-4 4z"></path>
                    </svg>
                    Import from Excel
                  </button>
                </MenuItem>
                <MenuItem v-slot="{ active }">
                  <button
                    @click="showBatchImageUpload = true"
                    :class="[
                      active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                      'group flex items-center px-4 py-2 text-sm w-full text-left'
                    ]"
                  >
                    <svg class="mr-3 h-4 w-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Batch Upload Images
                  </button>
                </MenuItem>
                <MenuItem v-slot="{ active }">
                  <button
                    @click="showFolderUpload = true"
                    :class="[
                      active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                      'group flex items-center px-4 py-2 text-sm w-full text-left'
                    ]"
                  >
                    <svg class="mr-3 h-4 w-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    Upload ECO-MiC Folder
                  </button>
                </MenuItem>
              </div>
            </MenuItems>
          </transition>
        </Menu>
      </div>
    </div>

    <!-- Upload Form Modal -->
    <TransitionRoot appear :show="showUploadForm" as="template">
      <Dialog as="div" @close="closeUploadForm" class="relative z-50">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
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
              <DialogPanel class="w-full max-w-6xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                <div class="flex items-center justify-between p-6 border-b border-gray-200">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                    Upload New Document
                  </DialogTitle>
                  <button
                    @click="closeUploadForm"
                    class="rounded-md bg-white text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div class="p-6">
                  <DocumentUploadForm @upload-complete="handleUploadComplete" @cancel="closeUploadForm" />
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Excel Batch Import Modal -->
    <TransitionRoot appear :show="showExcelBatchImport" as="template">
      <Dialog as="div" @close="closeExcelBatchImport" class="relative z-50">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
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
                <div class="flex items-center justify-between p-6 border-b border-gray-200">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                    Batch Import from Excel
                  </DialogTitle>
                  <button
                    @click="closeExcelBatchImport"
                    class="rounded-md bg-white text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div class="p-6">
                  <ExcelBatchImport @import-complete="handleExcelImportComplete" @cancel="closeExcelBatchImport" />
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Batch Image Upload Modal -->
    <TransitionRoot appear :show="showBatchImageUpload" as="template">
      <Dialog as="div" @close="closeBatchImageUpload" class="relative z-50">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
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
              <DialogPanel class="w-full max-w-6xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                <div class="flex items-center justify-between p-6 border-b border-gray-200">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                    Batch Upload Images
                  </DialogTitle>
                  <button
                    @click="closeBatchImageUpload"
                    class="rounded-md bg-white text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div class="p-6">
                  <BatchImageUpload 
                    @upload-complete="handleBatchImageUploadComplete" 
                    @cancel="closeBatchImageUpload" 
                  />
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Folder Upload Modal -->
    <TransitionRoot appear :show="showFolderUpload" as="template">
      <Dialog as="div" @close="closeFolderUpload" class="relative z-50">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
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
              <DialogPanel class="w-full max-w-6xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                <div class="flex items-center justify-between p-6 border-b border-gray-200">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                    Upload ECO-MiC Folder Structure
                  </DialogTitle>
                  <button
                    @click="closeFolderUpload"
                    class="rounded-md bg-white text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div class="p-6">
                  <FolderUpload
                    @success="handleFolderUploadComplete"
                    @cancel="closeFolderUpload"
                  />
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Delete Confirmation Modal -->
    <TransitionRoot appear :show="showDeleteConfirm" as="template">
      <Dialog as="div" @close="cancelDelete" class="relative z-50">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
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
              <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                <div class="p-6">
                  <div class="flex items-center space-x-4">
                    <div class="flex-shrink-0">
                      <svg class="h-10 w-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z"></path>
                      </svg>
                    </div>
                    <div class="flex-1">
                      <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                        Delete Documents
                      </DialogTitle>
                      <div class="mt-2">
                        <p class="text-sm text-gray-500">
                          Are you sure you want to delete <span class="font-semibold text-gray-900">{{ selectedDocuments.length }}</span> document{{ selectedDocuments.length !== 1 ? 's' : '' }}? This action cannot be undone.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="bg-gray-50 px-6 py-4 sm:flex sm:flex-row-reverse sm:space-x-reverse sm:space-x-3">
                  <button
                    @click="confirmDelete"
                    :disabled="isDeleting"
                    :class="[
                      'inline-flex w-full justify-center rounded-md border border-transparent px-4 py-2 text-base font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm transition-colors',
                      isDeleting
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
                    ]"
                  >
                    <svg v-if="isDeleting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ isDeleting ? 'Deleting...' : 'Delete' }}
                  </button>
                  <button
                    @click="cancelDelete"
                    :disabled="isDeleting"
                    class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 sm:mt-0 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Document Detail Modal -->
    <DocumentDetailModal 
      v-if="selectedDocument" 
      :document="selectedDocument" 
      @close="selectedDocument = null" 
      @documentUpdated="handleDocumentUpdated"
      @documentDeleted="handleDocumentDeleted"
    />

    <!-- Bulk Actions Bar -->
    <div v-if="selectedDocuments.length > 0" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <span class="text-sm font-medium text-blue-900">
            {{ selectedDocuments.length }} document{{ selectedDocuments.length !== 1 ? 's' : '' }} selected
          </span>
        </div>
        <div class="flex items-center space-x-3">
          <button
            @click="exportSelectedCSV"
            class="inline-flex items-center px-3 py-2 border border-blue-300 shadow-sm text-sm leading-4 font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Export CSV
          </button>
          <button
            @click="exportSelectedMETSXML"
            class="inline-flex items-center px-3 py-2 border border-blue-300 shadow-sm text-sm leading-4 font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Export METS XML
          </button>
          <button
            @click="downloadSelectedArchives"
            class="inline-flex items-center px-3 py-2 border border-blue-300 shadow-sm text-sm leading-4 font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
            </svg>
            Download Archives
          </button>
          <button
            @click="deleteSelectedDocuments"
            class="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            Delete Selected
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="flex items-center space-x-2">
        <svg class="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-gray-600">Loading documents...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error loading documents</h3>
          <div class="mt-2 text-sm text-red-700">{{ error }}</div>
          <div class="mt-4">
            <button
              @click="loadDocuments"
              class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Documents Table -->
    <div v-else class="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
      <div v-if="documents.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No documents</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by uploading your first document.</p>
        <div class="mt-6">
          <button
            @click="showUploadForm = true"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            Upload Document
          </button>
        </div>
      </div>

      <div v-else>
        <!-- Ensure minimum height for dropdown visibility -->
        <div class="overflow-x-auto min-h-[400px] relative" style="overflow-y: visible;">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8">
                  <input
                    type="checkbox"
                    :checked="allSelected"
                    @change="toggleAllSelection"
                    class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 sm:left-6"
                  />
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Logical ID
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Archive
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pages
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Files
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th scope="col" class="relative px-6 py-3">
                  <span class="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="document in documents"
                :key="document.id"
                class="hover:bg-gray-50 cursor-pointer"
                @click="openDocumentDetail(document)"
              >
                <td class="relative w-12 px-6 sm:w-16 sm:px-8" @click.stop>
                  <input
                    type="checkbox"
                    :value="document.id"
                    v-model="selectedDocuments"
                    class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 sm:left-6"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ document.logical_id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ document.title || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ document.archive_name || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span v-if="document.document_type" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {{ document.document_type }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ document.total_pages || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ document.file_count }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(document.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium relative" @click.stop style="overflow: visible;">
                  <div class="flex items-center space-x-2">
                    <button
                      @click="viewDocument(document)"
                      class="text-blue-600 hover:text-blue-900 transition-colors"
                      title="View Details"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                      </svg>
                    </button>
                    
                    <!-- Actions Menu -->
                    <Menu as="div" class="relative inline-block text-left">
                      <div>
                        <MenuButton class="text-gray-400 hover:text-gray-600 transition-colors">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                          </svg>
                        </MenuButton>
                      </div>

                      <transition
                        enter-active-class="transition duration-100 ease-out"
                        enter-from-class="transform scale-95 opacity-0"
                        enter-to-class="transform scale-100 opacity-100"
                        leave-active-class="transition duration-75 ease-in"
                        leave-from-class="transform scale-100 opacity-100"
                        leave-to-class="transform scale-95 opacity-0"
                      >
                        <MenuItems class="absolute right-0 z-50 mt-2 w-48 origin-top-right bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                          <div class="py-1">
                            <MenuItem v-slot="{ active }">
                              <button
                                @click="exportMetadataCSV(document.id)"
                                :class="[
                                  active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                                  'group flex items-center px-4 py-2 text-sm w-full text-left'
                                ]"
                              >
                                <svg class="mr-3 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                                Export CSV
                              </button>
                            </MenuItem>
                            <MenuItem v-slot="{ active }">
                              <button
                                @click="exportMETSXML(document.id)"
                                :class="[
                                  active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                                  'group flex items-center px-4 py-2 text-sm w-full text-left'
                                ]"
                              >
                                <svg class="mr-3 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                                Export METS XML
                              </button>
                            </MenuItem>
                            <MenuItem v-slot="{ active }">
                              <button
                                @click="downloadFiles(document.id)"
                                :class="[
                                  active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                                  'group flex items-center px-4 py-2 text-sm w-full text-left'
                                ]"
                              >
                                <svg class="mr-3 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                                Download Files
                              </button>
                            </MenuItem>
                            <MenuItem v-slot="{ active }">
                              <button
                                @click="downloadArchive(document.id)"
                                :class="[
                                  active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                                  'group flex items-center px-4 py-2 text-sm w-full text-left'
                                ]"
                              >
                                <svg class="mr-3 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                                </svg>
                                Download Archive
                              </button>
                            </MenuItem>
                          </div>
                        </MenuItems>
                      </transition>
                    </Menu>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div class="flex items-center justify-between">
            <div class="flex-1 flex justify-between sm:hidden">
              <button
                @click="goToPage(currentPage - 1)"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                @click="goToPage(currentPage + 1)"
                :disabled="currentPage === totalPages"
                class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p class="text-sm text-gray-700">
                  Showing page
                  <span class="font-medium">{{ currentPage }}</span>
                  of
                  <span class="font-medium">{{ totalPages }}</span>
                  ({{ documents.length }} documents)
                </p>
              </div>
              <div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    @click="goToPage(currentPage - 1)"
                    :disabled="currentPage === 1"
                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span class="sr-only">Previous</span>
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                    </svg>
                  </button>
                  <button
                    @click="goToPage(currentPage + 1)"
                    :disabled="currentPage === totalPages"
                    class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span class="sr-only">Next</span>
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
} from '@headlessui/vue'
import DocumentUploadForm from './DocumentUploadForm.vue'
import DocumentDetailModal from './DocumentDetailModal.vue'
import ExcelBatchImport from './ExcelBatchImport.vue'
import BatchImageUpload from './BatchImageUpload.vue'
import FolderUpload from './FolderUpload.vue'
import axios from 'axios'

export default {
  name: 'DocumentsManager',
  components: {
    DocumentUploadForm,
    DocumentDetailModal,
    ExcelBatchImport,
    BatchImageUpload,
    FolderUpload,
    Dialog,
    DialogPanel,
    DialogTitle,
    TransitionChild,
    TransitionRoot,
    Menu,
    MenuButton,
    MenuItem,
    MenuItems,
  },
  setup() {
    const authStore = useAuthStore()
    const documents = ref([])
    const selectedDocuments = ref([])
    const selectedDocument = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const showUploadForm = ref(false)
    const showExcelBatchImport = ref(false)
    const showBatchImageUpload = ref(false)
    const showFolderUpload = ref(false)
    const showDeleteConfirm = ref(false)
    const isDeleting = ref(false)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const pageSize = 20

    const allSelected = computed(() => {
      return documents.value.length > 0 && selectedDocuments.value.length === documents.value.length
    })

    const loadDocuments = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents`, {
          params: {
            page: currentPage.value,
            size: pageSize
          },
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        documents.value = response.data.documents || response.data.items || response.data
        
        if (response.data.total_pages) {
          totalPages.value = response.data.total_pages
        } else if (response.data.pages) {
          totalPages.value = response.data.pages
        }
        
      } catch (err) {
        console.error('Error loading documents:', err)
        error.value = err.response?.data?.detail || err.message || 'Failed to load documents'
      } finally {
        loading.value = false
      }
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

    const toggleAllSelection = () => {
      if (allSelected.value) {
        selectedDocuments.value = []
      } else {
        selectedDocuments.value = documents.value.map(doc => doc.id)
      }
    }

    const closeUploadForm = () => {
      showUploadForm.value = false
    }

    const closeExcelBatchImport = () => {
      showExcelBatchImport.value = false
    }

    const closeBatchImageUpload = () => {
      showBatchImageUpload.value = false
    }

    const closeFolderUpload = () => {
      showFolderUpload.value = false
    }

    const handleUploadComplete = () => {
      closeUploadForm()
      loadDocuments()
    }

    const handleExcelImportComplete = () => {
      closeExcelBatchImport()
      loadDocuments()
    }

    const handleBatchImageUploadComplete = () => {
      closeBatchImageUpload()
      loadDocuments()
    }

    const handleFolderUploadComplete = () => {
      closeFolderUpload()
      loadDocuments()
    }

    const viewDocument = async (document) => {
      await loadDocumentDetails(document.id)
    }

    const openDocumentDetail = async (document) => {
      await loadDocumentDetails(document.id)
    }

    const loadDocumentDetails = async (documentId) => {
      try {
        loading.value = true
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents/${documentId}`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        selectedDocument.value = response.data
      } catch (err) {
        console.error('Error loading document details:', err)
        alert('Failed to load document details: ' + (err.response?.data?.detail || err.message))
      } finally {
        loading.value = false
      }
    }

    const handleDocumentUpdated = (updatedDocument) => {
      const index = documents.value.findIndex(doc => doc.id === updatedDocument.id)
      if (index !== -1) {
        documents.value[index] = updatedDocument
      }
    }

    const handleDocumentDeleted = (deletedDocumentId) => {
      documents.value = documents.value.filter(doc => doc.id !== deletedDocumentId)
      selectedDocument.value = null
    }

    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadDocuments()
      }
    }

    // Export and download methods
    const exportSelectedCSV = async () => {
      if (selectedDocuments.value.length === 0) return
      
      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/documents/export/csv`, {
          document_ids: selectedDocuments.value
        }, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          },
          responseType: 'blob'
        })
        
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Extract filename from Content-Disposition header if available
        let filename = 'documents.csv' // fallback
        const contentDisposition = response.headers['content-disposition']
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename=([^;]+)/)
          if (filenameMatch) {
            filename = filenameMatch[1].replace(/"/g, '') // remove quotes if present
          }
        }
        
        link.download = filename
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error exporting CSV:', err)
        alert('Failed to export CSV: ' + (err.response?.data?.detail || err.message))
      }
    }

    const exportSelectedMETSXML = async () => {
      if (selectedDocuments.value.length === 0) return
      
      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/documents/export/mets`, {
          document_ids: selectedDocuments.value
        }, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          },
          responseType: 'blob'
        })
        
        const blob = new Blob([response.data], { type: 'application/zip' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'documents_mets.zip'
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error exporting METS XML:', err)
        alert('Failed to export METS XML: ' + (err.response?.data?.detail || err.message))
      }
    }

    const downloadSelectedArchives = async () => {
      if (selectedDocuments.value.length === 0) return
      
      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/documents/download/archives`, {
          document_ids: selectedDocuments.value
        }, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          },
          responseType: 'blob'
        })
        
        const blob = new Blob([response.data], { type: 'application/zip' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'documents_archives.zip'
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error downloading archives:', err)
        alert('Failed to download archives: ' + (err.response?.data?.detail || err.message))
      }
    }

    const deleteSelectedDocuments = async () => {
      if (selectedDocuments.value.length === 0) return
      
      // Show confirmation modal instead of browser confirm
      showDeleteConfirm.value = true
    }

    const confirmDelete = async () => {
      showDeleteConfirm.value = false
      isDeleting.value = true
      
      try {
        await axios.delete(`${import.meta.env.VITE_API_URL}/api/documents/batch`, {
          data: {
            document_ids: selectedDocuments.value
          },
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        // Remove deleted documents from the list
        documents.value = documents.value.filter(doc => !selectedDocuments.value.includes(doc.id))
        selectedDocuments.value = []
        
        // You could add a success toast notification here instead of alert
        alert('Documents deleted successfully')
      } catch (err) {
        console.error('Error deleting documents:', err)
        alert('Failed to delete documents: ' + (err.response?.data?.detail || err.message))
      } finally {
        isDeleting.value = false
      }
    }

    const cancelDelete = () => {
      showDeleteConfirm.value = false
    }

    const exportMetadataCSV = async (documentId) => {
      try {
        // Find the document in our list to get its logical_id
        const doc = documents.value.find(d => d.id === documentId)
        const logicalId = doc?.logical_id || `document_${documentId}`
        
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents/${documentId}/export/csv`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          },
          responseType: 'blob'
        })
        
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Use logical_id directly for the filename
        const sanitizedLogicalId = logicalId.replace(/[^a-zA-Z0-9\-_\.]/g, '_')
        const filename = `${sanitizedLogicalId}_metadata.csv`
        
        link.download = filename
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error exporting CSV:', err)
        alert('Failed to export CSV: ' + (err.response?.data?.detail || err.message))
      }
    }

    const exportMETSXML = async (documentId) => {
      try {
        // Find the document in our list to get its logical_id
        const doc = documents.value.find(d => d.id === documentId)
        const logicalId = doc?.logical_id || `document_${documentId}`
        
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents/${documentId}/export/mets`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          },
          responseType: 'blob'
        })
        
        const blob = new Blob([response.data], { type: 'application/xml' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Use logical_id for the filename
        const sanitizedLogicalId = logicalId.replace(/[^a-zA-Z0-9\-_\.]/g, '_')
        const filename = `${sanitizedLogicalId}_mets.xml`
        
        link.download = filename
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error exporting METS XML:', err)
        alert('Failed to export METS XML: ' + (err.response?.data?.detail || err.message))
      }
    }

    const downloadFiles = async (documentId) => {
      try {
        // Find the document in our list to get its logical_id
        const doc = documents.value.find(d => d.id === documentId)
        const logicalId = doc?.logical_id || `document_${documentId}`
        
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents/${documentId}/download/files`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          },
          responseType: 'blob'
        })
        
        const blob = new Blob([response.data], { type: 'application/zip' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Use logical_id for the filename
        const sanitizedLogicalId = logicalId.replace(/[^a-zA-Z0-9\-_\.]/g, '_')
        const filename = `${sanitizedLogicalId}_files.zip`
        
        link.download = filename
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error downloading files:', err)
        alert('Failed to download files: ' + (err.response?.data?.detail || err.message))
      }
    }

    const downloadArchive = async (documentId) => {
      try {
        // Find the document in our list to get its logical_id
        const doc = documents.value.find(d => d.id === documentId)
        const logicalId = doc?.logical_id || `document_${documentId}`
        
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/documents/${documentId}/download/archive`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          },
          responseType: 'blob'
        })
        
        const blob = new Blob([response.data], { type: 'application/zip' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Use logical_id for the filename
        const sanitizedLogicalId = logicalId.replace(/[^a-zA-Z0-9\-_\.]/g, '_')
        const filename = `${sanitizedLogicalId}_archive.zip`
        
        link.download = filename
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error downloading archive:', err)
        alert('Failed to download archive: ' + (err.response?.data?.detail || err.message))
      }
    }

    onMounted(() => {
      loadDocuments()
    })

    return {
      documents,
      selectedDocuments,
      selectedDocument,
      loading,
      error,
      showUploadForm,
      showExcelBatchImport,
      showBatchImageUpload,
      showFolderUpload,
      showDeleteConfirm,
      isDeleting,
      currentPage,
      totalPages,
      allSelected,
      loadDocuments,
      formatDate,
      toggleAllSelection,
      closeUploadForm,
      closeExcelBatchImport,
      closeBatchImageUpload,
      closeFolderUpload,
      handleUploadComplete,
      handleExcelImportComplete,
      handleBatchImageUploadComplete,
      handleFolderUploadComplete,
      viewDocument,
      openDocumentDetail,
      handleDocumentUpdated,
      handleDocumentDeleted,
      goToPage,
      exportSelectedCSV,
      exportSelectedMETSXML,
      downloadSelectedArchives,
      deleteSelectedDocuments,
      confirmDelete,
      cancelDelete,
      exportMetadataCSV,
      exportMETSXML,
      downloadFiles,
      downloadArchive
    }
  }
}
</script>
