<!-- DropFile.vue -->
<template>
  <div>
    <Button @click="selectAndProcess">选择文件并处理</Button>
    <!-- <AspectRatio :ratio="16 / 9">
      <img :src="imgSrc" alt="本地图片" class="rounded-md object-cover w-full h-full bg-amber-100">
    </AspectRatio> -->
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '@/components/ui/button/Button.vue';
// import { AspectRatio } from '@/components/ui/aspect-ratio'
import { toast } from 'vue-sonner'
import 'vue-sonner/style.css'

const imgSrc = ref('')
const { ipcRenderer } = window

ipcRenderer.on('py:output', (_, boxedPath: string) => {
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
  // toast.error('错误！', {
  //   description: err,
  //   action: {
  //     label: 'Details',
  //     onClick: () => console.log(err),
  //   },
  // })
})


async function selectAndProcess() {
  // 调用主进程的 select-files 处理器，弹出文件选择对话框
  const paths = await (ipcRenderer as any).selectFiles()

  // 逐个处理选中的文件路径
  console.log('原始路径:', paths[0])
  const boxedPath = await (ipcRenderer as any).processFile(paths[0])
  console.log('Python 处理后的路径:', boxedPath)
  imgSrc.value = "src/img/frame_000000.jpg"
}
</script>