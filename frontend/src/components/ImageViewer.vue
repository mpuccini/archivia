<template>
  <div class="image-viewer-overlay" @click="close" v-if="isVisible">
    <div class="image-viewer-container" @click.stop>
      <div class="image-viewer-header">
        <h3>{{ filename }}</h3>
        <div class="image-viewer-controls">
          <button @click="zoomOut" class="btn btn-sm btn-secondary" :disabled="scale <= 0.1">
            🔍-
          </button>
          <span class="zoom-level">{{ Math.round(scale * 100) }}%</span>
          <button @click="zoomIn" class="btn btn-sm btn-secondary" :disabled="scale >= 5">
            🔍+
          </button>
          <button @click="resetZoom" class="btn btn-sm btn-secondary">
            Reset
          </button>
          <button @click="close" class="btn btn-sm btn-secondary">
            ✕
          </button>
        </div>
      </div>
      
      <div 
        class="image-viewer-content" 
        ref="viewerContent"
        @wheel="handleWheel"
        @mousedown="startPan"
        @mousemove="handlePan"
        @mouseup="endPan"
        @mouseleave="endPan"
      >
        <img 
          :src="imageUrl" 
          :alt="filename"
          ref="imageElement"
          :style="imageStyle"
          @load="onImageLoad"
          @dragstart.prevent
        />
      </div>
      
      <div class="image-viewer-footer">
        <div class="image-info">
          <span v-if="imageWidth && imageHeight">
            {{ imageWidth }} × {{ imageHeight }} pixels
          </span>
          <span v-if="fileSize">
            • {{ formatFileSize(fileSize) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick } from 'vue'

export default {
  name: 'ImageViewer',
  props: {
    imageUrl: {
      type: String,
      required: true
    },
    filename: {
      type: String,
      default: 'Image'
    },
    imageWidth: {
      type: Number,
      default: null
    },
    imageHeight: {
      type: Number,
      default: null
    },
    fileSize: {
      type: Number,
      default: null
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const scale = ref(1)
    const translateX = ref(0)
    const translateY = ref(0)
    const isPanning = ref(false)
    const lastPanX = ref(0)
    const lastPanY = ref(0)
    const isVisible = ref(false)
    const imageElement = ref(null)
    const viewerContent = ref(null)
    const naturalWidth = ref(0)
    const naturalHeight = ref(0)

    // Watch for visibility changes
    watch(() => props.visible, (newVisible) => {
      isVisible.value = newVisible
      if (newVisible) {
        resetZoom()
        // Prevent body scroll when viewer is open
        document.body.style.overflow = 'hidden'
      } else {
        // Restore body scroll when viewer is closed
        document.body.style.overflow = ''
      }
    })

    const imageStyle = computed(() => ({
      transform: `scale(${scale.value}) translate(${translateX.value}px, ${translateY.value}px)`,
      cursor: isPanning.value ? 'grabbing' : (scale.value > 1 ? 'grab' : 'default'),
      transition: isPanning.value ? 'none' : 'transform 0.2s ease-out'
    }))

    const onImageLoad = () => {
      if (imageElement.value) {
        naturalWidth.value = imageElement.value.naturalWidth
        naturalHeight.value = imageElement.value.naturalHeight
      }
    }

    const zoomIn = () => {
      if (scale.value < 5) {
        scale.value = Math.min(5, scale.value * 1.5)
      }
    }

    const zoomOut = () => {
      if (scale.value > 0.1) {
        scale.value = Math.max(0.1, scale.value / 1.5)
        // Adjust translation to keep image centered when zooming out
        if (scale.value <= 1) {
          translateX.value = 0
          translateY.value = 0
        }
      }
    }

    const resetZoom = () => {
      scale.value = 1
      translateX.value = 0
      translateY.value = 0
    }

    const handleWheel = (event) => {
      event.preventDefault()
      const delta = event.deltaY > 0 ? -1 : 1
      
      if (delta > 0) {
        zoomIn()
      } else {
        zoomOut()
      }
    }

    const startPan = (event) => {
      if (scale.value > 1) {
        isPanning.value = true
        lastPanX.value = event.clientX
        lastPanY.value = event.clientY
        event.preventDefault()
      }
    }

    const handlePan = (event) => {
      if (isPanning.value && scale.value > 1) {
        const deltaX = event.clientX - lastPanX.value
        const deltaY = event.clientY - lastPanY.value
        
        translateX.value += deltaX / scale.value
        translateY.value += deltaY / scale.value
        
        lastPanX.value = event.clientX
        lastPanY.value = event.clientY
        event.preventDefault()
      }
    }

    const endPan = () => {
      isPanning.value = false
    }

    const close = () => {
      emit('close')
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return 'N/A'
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      if (bytes === 0) return '0 Bytes'
      let i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
      i = Math.min(i, sizes.length - 1)
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }

    return {
      scale,
      translateX,
      translateY,
      isPanning,
      isVisible,
      imageElement,
      viewerContent,
      imageStyle,
      naturalWidth,
      naturalHeight,
      onImageLoad,
      zoomIn,
      zoomOut,
      resetZoom,
      handleWheel,
      startPan,
      handlePan,
      endPan,
      close,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.image-viewer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.image-viewer-container {
  width: 95vw;
  height: 95vh;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.image-viewer-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
  flex-shrink: 0;
}

.image-viewer-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 50%;
}

.image-viewer-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.zoom-level {
  font-size: 0.875rem;
  color: #666;
  min-width: 50px;
  text-align: center;
}

.image-viewer-content {
  flex: 1;
  overflow: hidden;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f5f5;
  user-select: none;
}

.image-viewer-content img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transform-origin: center center;
}

.image-viewer-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #eee;
  background: #f8f9fa;
  flex-shrink: 0;
}

.image-info {
  font-size: 0.875rem;
  color: #666;
  text-align: center;
}

.btn {
  padding: 0.375rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  background-color: #6c757d;
  color: white;
  transition: background-color 0.2s;
}

.btn:hover:not(:disabled) {
  background-color: #545b62;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .image-viewer-container {
    width: 100vw;
    height: 100vh;
    border-radius: 0;
  }
  
  .image-viewer-header {
    padding: 0.75rem;
  }
  
  .image-viewer-header h3 {
    font-size: 1rem;
    max-width: 40%;
  }
  
  .image-viewer-controls {
    gap: 0.25rem;
  }
  
  .btn-sm {
    padding: 0.2rem 0.4rem;
    font-size: 0.7rem;
  }
  
  .zoom-level {
    font-size: 0.75rem;
    min-width: 40px;
  }
}
</style>
