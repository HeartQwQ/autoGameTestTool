<script setup lang="ts">
import Layouts from './components/sidebar/Layouts.vue'
import { Sonner } from '@/components/ui/sonner'
import { toast } from 'vue-sonner'
import 'vue-sonner/style.css'
const { ipcRenderer } = window

// 监听Python输出
ipcRenderer.on('py:info', (_, boxedPath: string) => {
  console.log('Python 输出:', boxedPath)
  toast.info('提示：', {
    description: boxedPath,
    action: {
      label: 'Undo',
      onClick: () => console.log('Undo'),
    },
  })
})

// 监听错误
ipcRenderer.on('py:error', (_, err) => {
  console.error('Python 错误:', err)
  toast.error('错误！', {
    description: err,
    action: {
      label: 'Details',
      onClick: () => console.log(err),
    },
  })
})
</script>

<template>
  <Layouts />
  <Sonner position="top-right"/>
</template>

<style scoped>

</style>
