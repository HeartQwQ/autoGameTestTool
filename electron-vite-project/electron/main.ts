// 引入 Electron 核心模块
import { app, BrowserWindow, ipcMain, dialog } from 'electron'
// 用于将 import.meta.url 转换为文件路径（兼容 ES 模块）
import { fileURLToPath } from 'node:url'
// 用于启动子进程（如调用 Python 脚本）
import { spawn } from 'child_process'
// Node.js 路径处理模块
import path from 'node:path'

// 获取当前主进程脚本（main.js）所在目录（即 dist-electron）
const __dirname = path.dirname(fileURLToPath(import.meta.url))
// 已构建的目录结构
// ├─┬─┬ dist
// │ │ └── index.html
// │ │
// │ ├─┬ dist-electron
// │ │ ├── main.js
// │ │ └── preload.mjs

// 设置环境变量 APP_ROOT: 项目根目录
process.env.APP_ROOT = path.join(__dirname, '..')
console.log('主进程:', __dirname)
console.log('项目根目录:', process.env.APP_ROOT)

// 🚧 Use ['ENV_NAME'] avoid vite:define plugin - Vite@2.x
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
// 主进程构建输出目录（dist-electron）
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
// 渲染进程构建输出目录（dist）
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

// 设置 VITE_PUBLIC 路径：
// - 开发模式下指向 public 目录
// - 生产模式下指向 RENDERER_DIST（即 dist）
process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

// 创建主窗口变量及函数
let win: BrowserWindow | null
function createWindow() {
  // 创建一个新的 BrowserWindow 实例
  win = new BrowserWindow({
    width: 1280,  // 窗口宽度
    height: 760, // 窗口高度
    // 设置窗口图标（Electron 会自动处理不同平台格式）
    icon: path.join(process.env.VITE_PUBLIC, 'electron-vite.svg'),
    // WebPreferences 配置渲染进程的安全与集成功能
    webPreferences: {
      // 预加载脚本路径（在渲染进程加载前执行）
      preload: path.join(__dirname, 'preload.mjs'),
      // 禁用 Node.js 集成（提高安全性）
      nodeIntegration: false,
      // 启用上下文隔离（推荐，与 preload 配合使用）
      contextIsolation: true,
    }
  })

  // 当页面加载完成后，向渲染进程发送一条消息（含当前时间）
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
  })

  // 根据是否处于开发模式，加载不同内容：
  if (VITE_DEV_SERVER_URL) {
    // 开发模式：加载 Vite 开发服务器的 URL（如 http://localhost:5173）
    win.loadURL(VITE_DEV_SERVER_URL)
    win.webContents.openDevTools()
  } else {
    // 生产模式：加载本地构建好的 index.html
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }
}

// 当所有窗口关闭时的行为（macOS 除外）
app.on('window-all-closed', () => {
  // 在 macOS 上，通常应用会保持运行，直到用户手动退出（Cmd+Q）
  if (process.platform !== 'darwin') {
    app.quit()
    win = null // 清理窗口引用
  }
})

// 当应用被激活时（macOS 点击 dock 图标）
app.on('activate', () => {
  // 如果没有窗口打开，则重新创建一个
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// whenReady: 当 Electron 应用准备就绪后执行
// createWindow: 创建主窗口
app.whenReady().then(createWindow)

// IPC 主进程监听：渲染进程请求选择文件
ipcMain.handle('select-files', async () => {
  // 弹出系统文件选择对话框
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openFile'],  // 允许打开文件 + 多选
    // properties: ['openFile', 'multiSelections'],  // 允许打开文件 + 多选
    // filters: [{ name: 'Media', extensions: ['mp4', 'mkv', 'jpg', 'png'] }]  // 限制文件类型
  })
  // 如果用户取消，返回空数组；否则返回选中的绝对路径数组
  return canceled ? [] : filePaths // 绝对路径数组
})

// IPC 主进程监听：调用 Python 脚本处理文件
ipcMain.handle('py:process', async (_, filePath: string) => {
  const userDataPath = app.getPath('userData') // 👈 获取可写目录
  let pyScriptPath = null
  // 启动 Python 子进程，执行 main.py 并传入文件路径
  if (VITE_DEV_SERVER_URL) {
    pyScriptPath = path.join(app.getAppPath(), 'src', 'pythons', 'main.py')
  } else {
    pyScriptPath = path.join(process.resourcesPath, 'pythons', 'main.py')
  }

  console.log('调用 Python 脚本:', pyScriptPath, filePath, userDataPath)

  const py = spawn('python', [
    '-u',
    pyScriptPath,
    filePath,
    userDataPath
  ])

  // 监听 Python 标准输出, 并将输出通过 IPC 发送回渲染进程
  py.stdout.on('data', (chunk) => {
    _.sender.send('py:output', chunk.toString('utf8'))
  })
  // 监听 Python 错误输出, 并将错误通过 IPC 发送回渲染进程
  py.stderr.on('data', (chunk) => {
    console.error('Python stderr:', chunk.toString('utf8'))
    _.sender.send('py:error', chunk.toString('utf8')) // 可选：推送错误
  })

  return new Promise((resolve, reject) => {
    // 子进程退出时处理结果
    py.on('close', (code) => {
      // 非零退出码视为错误
      if (code !== 0) return reject(new Error(`Python exit ${code}`))
      // 成功时返回 Python 的 stdout 内容（去除首尾空白）
      resolve("处理完成!")
    })
  })
})