<template>
    <div>
        <div class="flex justify-between">
          <div class="flex flex-1 flex-wrap gap-2">
            <!-- 开始时间 -->
            <FormField v-slot="{ componentField }" name="videoStart">
              <FormItem v-auto-animate class="w-full">
                <FormLabel>开始时间：</FormLabel>
                <FormControl>
                  <Input type="number" v-bind="componentField" class="hidden" />
                </FormControl>
              </FormItem>
            </FormField>
            <!-- 开始分 -->
            <FormField v-slot="{ componentField }" name="videoStart_MM">
              <FormItem v-auto-animate class="flex items-center">
                <FormControl>
                  <Input type="number" min="0" max="59" v-bind="componentField" class="w-14 text-right" />
                </FormControl>
                <FormLabel>分</FormLabel>
              </FormItem>
            </FormField>
            <!-- 开始秒 -->
            <FormField v-slot="{ componentField }" name="videoStart_SS">
              <FormItem v-auto-animate class="flex items-center">
                <FormControl>
                  <Input type="number" min="0" max="59" v-bind="componentField" class="w-14 text-right" />
                </FormControl>
                <FormLabel>秒</FormLabel>
              </FormItem>
            </FormField>
            <FormField name="videoStart">
              <FormItem class="mt-2">
                <FormMessage class="text-destructive text-sm">
                  <!-- {{ joinErrors([mmError, ssError, startError]) }} -->
                </FormMessage>
              </FormItem>
            </FormField>
          </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { watchEffect } from 'vue'
import { useForm, useFieldError  } from 'vee-validate'
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

let maxSeconds = 1

const formSchema = toTypedSchema(z.object({
  videoPath: z.any().refine(files => {
    return (
      files != null &&
      typeof files === 'object' &&
      'length' in files &&
      files.length > 0
    )
  }, { message: '请选择一个视频文件' }),
  videoStart: z.coerce.number().min(0).max(maxSeconds, `开始时间不能超过视频总时长（${maxSeconds} 秒）`),
  videoStart_MM: z.coerce.number().min(0).max(59),
  videoStart_SS: z.coerce.number().min(0).max(59),
}))


const  { handleSubmit, setFieldValue, values } = useForm({
  validationSchema: formSchema,
  initialValues: {
    videoPath: null,
    videoStart: 1,
    videoStart_MM: 0,
    videoStart_SS: 1,
  }
})

const mmError  = useFieldError('videoStart_MM')
const ssError  = useFieldError('videoStart_SS')
const startError = useFieldError('videoStart')

// 把第一条非空错误拼出来即可
function joinErrors(errs: (string | undefined)[]) {
  return errs.find(e => !!e) || ''
}


watchEffect(() => {
  const mm = Number(values.videoStart_MM || 0)
  const ss = Number(values.videoStart_SS || 0)
  setFieldValue('videoStart', mm * 60 + ss)
})
</script>