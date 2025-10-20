<script setup lang="ts">
import { Button } from '@/components/ui/button'

import { invoke } from '@tauri-apps/api/core'
import { open } from '@tauri-apps/plugin-dialog';

const handleProcessVideo = async () => {
    // 1. 打开文件选择对话框（只允许视频）
    const filePath = await open({
        filters: [{
            name: '选择视频',
            extensions: ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv']
        }],
        multiple: false // 只选一个
    })

    if (!filePath) {
        console.log('No file selected')
        return
    }

    try {
        // 2. 调用 Rust 命令处理视频
        const resultStr = await invoke<string>('process_video', { videoPath: filePath })

        // 3. 解析 Python 返回的 JSON
        const result = JSON.parse(resultStr)

        if (result.status === 'success') {
            alert(`✅ 处理成功！\n输出路径: ${result.output_path}`)
        } else {
            alert(`❌ 处理失败: ${result.message}`)
        }
    } catch (error) {
        console.error('处理失败:', error)
        alert(`错误: ${error}`)
    }
}
</script>

<template>
    <Button @Click=handleProcessVideo>Run Python</Button>
</template>