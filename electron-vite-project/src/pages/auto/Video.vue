<template>
  <div class="flex gap-8">
    <div class="flex-1">
      <form @submit="onSubmit" class="flex flex-col gap-4">
        <FormField v-slot="{ componentField, value }" name="videoPath">
          <FormItem v-auto-animate>
            <FormLabel>视频：</FormLabel>
            <FormControl>
              <Input
                type="text"
                readonly
                placeholder="点击选择视频文件"
                class="cursor-pointer"
                :value="value"
                @click="() => handleSelectFile(componentField)"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <Button type="submit" @submit="onSubmit">
          提交
        </Button>
      </form>

    </div>
    <div class="flex-1">
      表格
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue';
import { Input } from '@/components/ui/input'
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { useField } from 'vee-validate'
import { vAutoAnimate } from "@formkit/auto-animate/vue"

// 表单
const onSubmit = ((values) => {
  console.log('表单已提交!', values)
})

const { ipcRenderer } = window

async function handleSelectFile(componentField: any) {
  // 调用主进程的 select-files 处理器，弹出文件选择对话框
  const paths = await ipcRenderer.invoke('select-files')
  const selectedPath = paths[0]
  componentField.onChange(selectedPath)

  if (!selectedPath) return

  const processedPath = await ipcRenderer.invoke('process-file', selectedPath)
  console.log(processedPath)
}
</script>