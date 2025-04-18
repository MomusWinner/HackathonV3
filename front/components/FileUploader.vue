<template>
  <Card>
    <div 
      class="border-2 border-dashed rounded-lg p-8 text-center transition-colors"
      :class="{
        'border-primary bg-primary/10': dragActive,
        'border-gray-300': !dragActive
      }"
      @dragover.prevent="handleDragOver"
      @dragleave="handleDragLeave"
      @drop.prevent="handleDrop"
      @click="() => $refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        multiple
        @change="onFileSelect"
      />

      <div class="flex flex-col items-center gap-4">
        <CloudUploadIcon class="h-8 w-8 text-gray-500" />
        <div>
          <p class="font-medium">Загрузить файл</p>
          <p class="text-sm text-gray-500 mt-1">
            Поддерживаемые форматы: PPTX, PDF (max {{ maxSizeMB }}MB)
          </p>
        </div>
      </div>
    </div>

    <!-- Selected files list -->
    <div v-if="files.length > 0" class="mt-6 space-y-2">
      <div 
        v-for="(file, index) in files"
        :key="index"
        class="flex items-center justify-between p-3 bg-white rounded-lg border"
      >
        <div class="flex items-center gap-3">
          <FileTextIcon class="h-5 w-5 text-gray-500" />
          <div>
            <p class="text-sm font-medium">{{ file.name }}</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          @click="removeFile(index)"
        >
          Remove
        </Button>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="mt-4 text-sm text-destructive">
      {{ error }}
    </div>
  </Card>
</template>

<script setup>
import { CloudUploadIcon, FileTextIcon } from 'lucide-vue-next'

const props = defineProps({
  maxFiles: {
    type: Number,
    default: 1
  },
  maxSizeMB: {
    type: Number,
    default: 50
  }
})

const emit = defineEmits(['files-selected'])

const files = ref([])
const dragActive = ref(false)
const error = ref(null)
const fileInput = ref(null)

const handleDragOver = () => {
  dragActive.value = true
}

const handleDragLeave = () => {
  dragActive.value = false
}

const handleDrop = (e) => {
  dragActive.value = false
  const droppedFiles = e.dataTransfer.files
  if (droppedFiles) {
    handleFiles(droppedFiles)
  }
}

const onFileSelect = (e) => {
  const selectedFiles = e.target.files
  if (selectedFiles) {
    handleFiles(selectedFiles)
  }
}

const handleFiles = (rawFiles) => {
  error.value = null
  const newFiles = Array.from(rawFiles)
  
  // Validate file count
  if (files.value.length + newFiles.length > props.maxFiles) {
    error.value = `Maximum ${props.maxFiles} files allowed`
    return
  }

  // Validate file size
  const maxSizeBytes = props.maxSizeMB * 1024 * 1024
  const invalidFiles = newFiles.filter(file => file.size > maxSizeBytes)
  if (invalidFiles.length > 0) {
    error.value = `Files exceed maximum size of ${props.maxSizeMB}MB`
    return
  }

  files.value = [...files.value, ...newFiles]
  emit('files-selected', files.value)
}

const removeFile = (index) => {
  files.value.splice(index, 1)
  emit('files-selected', files.value)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>
