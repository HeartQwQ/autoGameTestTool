<!-- DropFile.vue -->
<template>
  <div class="flex gap-8">
    <div class="flex-1">
      <form @submit="onSubmit" class="flex flex-col gap-4">
        <FormField v-slot="{ componentField }" name="videoPath">
          <FormItem v-auto-animate>
            <FormLabel>选择视频</FormLabel>
            <FormControl>
              <Input type="file" accept="video/*" @change="hVideoFileChange($event, componentField)" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <div class="flex justify-between">
          <div class="flex flex-1 flex-wrap gap-2">
            <!-- 开始时间 -->
            <FormField v-slot="{ componentField }" name="videoStart">
              <FormItem v-auto-animate class="w-full">
                <FormLabel>开始时间</FormLabel>
                <FormControl>
                  <Input type="number" v-bind="componentField" class="hidden" />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
            <!-- 开始分 -->
            <FormField v-slot="{ componentField }" name="videoStart_MM">
              <FormItem v-auto-animate class="flex items-center">
                <FormControl>
                  <Input type="number" min="0" max="59" v-bind="componentField" class="w-14 text-right" />
                </FormControl>
                <FormLabel>分</FormLabel>
                <FormMessage />
              </FormItem>
            </FormField>
            <!-- 开始秒 -->
            <FormField v-slot="{ componentField }" name="videoStart_SS">
              <FormItem v-auto-animate class="flex items-center">
                <FormControl>
                  <Input type="number" min="0" max="59" v-bind="componentField" class="w-14 text-right" />
                </FormControl>
                <FormLabel>秒</FormLabel>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>
        </div>
        <Button type="submit" @submit="onSubmit">
          提交
        </Button>
      </form>

    </div>
    <div class="flex-1">
      表格
    </div>
  </div>

  <!-- <Button @click="selectAndProcess">选择文件并处理</Button> -->
  <!-- <AspectRatio :ratio="16 / 9">
      <img :src="imgSrc" alt="本地图片" class="rounded-md object-cover w-full h-full bg-amber-100">
    </AspectRatio> -->
</template>

<script setup lang="ts">
import { ref } from 'vue'

import Button from '@/components/ui/button/Button.vue';
import { Input } from '@/components/ui/input'
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from '@/components/ui/number-field'

// 表单
import { useForm } from 'vee-validate'
import { vAutoAnimate } from "@formkit/auto-animate/vue"
import { toTypedSchema } from '@vee-validate/zod'
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import * as z from 'zod'
const formSchema = toTypedSchema(z.object({
  videoPath: z.any().refine(files => {
    return (
      files != null &&
      typeof files === 'object' &&
      'length' in files &&
      files.length > 0
    )
  }, { message: '请选择一个视频文件' }),
  videoStart: z.coerce.number().min(0),
  videoStart_MM: z.coerce.number().min(0).max(59),
  videoStart_SS: z.coerce.number().min(0).max(59),
  // videoEnd: z.coerce.number().min(1)
}))

const form = useForm({
  validationSchema: formSchema,
  initialValues: {
    videoPath: null,
    videoStart: 1,
    videoStart_MM: 0,
    videoStart_SS: 1,
    // videoEnd: 1,
  }
})

const hVideoFileChange = (event: Event, field: any) => {
  const files = (event.target as HTMLInputElement).files
  field.onChange(files)
}

const onSubmit = form.handleSubmit((values) => {
  console.log('表单已提交!', values)
})

import { toast } from 'vue-sonner'
import 'vue-sonner/style.css'

const imgSrc = ref('')
const { ipcRenderer } = window

// 监听Python输出
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