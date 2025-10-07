<!-- DropFile.vue -->
<template>
  <Button @click="selectAndProcess">选择文件并处理</Button>
  <!-- <img :src="imgSrc" style="width:100%;height:auto;" /> -->
  <div class="w-[450px]">
    <AspectRatio :ratio="16 / 9">
      <img :src="imgSrc" alt="本地图片" class="rounded-md object-cover w-full h-full bg-amber-100">
    </AspectRatio>
    <AspectRatio :ratio="16 / 9">
      <img src="../img/frame_000000.jpg" alt="本地图片" class="rounded-md object-cover w-full h-full bg-amber-100">
    </AspectRatio>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '@/components/ui/button/Button.vue';
import { AspectRatio } from '@/components/ui/aspect-ratio'

const imgSrc = ref('')

async function selectAndProcess() {
  const paths = await window.ipcRenderer.selectFiles()

  for (const p of paths) {
    console.log('原始路径:', p)
    const boxedPath = await window.ipcRenderer.processFile(p)
    console.log('Python 处理后的路径:', boxedPath)
    imgSrc.value = "src/img/frame_000000.jpg"
  }
}
</script>