import { app, BrowserWindow, ipcMain, dialog, protocol, net } from 'electron'
// import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import { spawn } from 'child_process'
import path from 'node:path'

// const require = createRequire(import.meta.url)
const __dirname = path.dirname(fileURLToPath(import.meta.url))
// The built directory structure
//
// ├─┬─┬ dist
// │ │ └── index.html
// │ │
// │ ├─┬ dist-electron
// │ │ ├── main.js
// │ │ └── preload.mjs
// │
process.env.APP_ROOT = path.join(__dirname, '..')

// 🚧 Use ['ENV_NAME'] avoid vite:define plugin - Vite@2.x
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

let win: BrowserWindow | null

function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC, 'electron-vite.svg'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
      nodeIntegration: false, contextIsolation: true,
    },
    // titleBarStyle: 'hidden',
    // // expose window controls in Windows/Linux
    // ...(process.platform !== 'darwin' ? { titleBarOverlay: true } : {})
  })

  // Test active push message to Renderer-process.
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
  } else {
    // win.loadFile('dist/index.html')
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }

  if (process.env.NODE_ENV === 'development') {
    win.webContents.openDevTools()
  }
}

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

protocol.registerSchemesAsPrivileged([
  {
    scheme: 'local_file',
    privileges: {
      standard: true,        // 遵守标准URI语法
      secure: true,          // 安全协议
      supportFetchAPI: true, // 支持Fetch API
      bypassCSP: true,       // 绕过内容安全策略
      stream: true,          // 支持流媒体
      corsEnabled: true      // 允许跨域
    }
  }
]);

app.whenReady().then(() => {
  console.log('App is ready, registering protocol...')

  /* ===== 注册本地文件协议 ===== */
  protocol.handle('local_file', (request) => {
    console.log('=== 协议处理被触发 ===');
    console.log('请求URL:', request.url);
    console.log('请求方法:', request.method);
    console.log('请求头:', JSON.stringify(Object.fromEntries(request.headers)));
    
    try {
      const urlObj = new URL(request.url);
      console.log('协议:', urlObj.protocol);
      console.log('主机:', urlObj.host);
      console.log('路径:', urlObj.pathname);
      
      let filePath = urlObj.pathname;
      
      // Windows 路径处理
      if (process.platform === 'win32' && filePath.startsWith('/')) {
        filePath = filePath.substring(1);
      }
      
      filePath = decodeURIComponent(filePath);
      console.log('解析后的文件路径:', filePath);
      
      // 返回文件
      return net.fetch('file:///' + filePath);
      
    } catch (error) {
      console.error('处理请求时出错:', error);
      return new Response('文件未找到', { 
        status: 404,
        headers: { 'Content-Type': 'text/plain' }
      });
    }
  })

  console.log(protocol.isProtocolHandled("local_file"))
  console.log('Protocol registered, now creating window...')

  createWindow() // 你的创建窗口函数
})

ipcMain.handle('select-files', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openFile', 'multiSelections'],
    filters: [{ name: 'Media', extensions: ['mp4', 'mkv', 'jpg', 'png'] }]
  })
  return canceled ? [] : filePaths // 绝对路径数组
})

ipcMain.handle('py:process', async (_, filePath: string) => {
  return new Promise((resolve, reject) => {
    const py = spawn('python', [path.join(__dirname, 'main.py'), filePath], {
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    })
    let out = ''
    py.stdout.on('data', (chunk) => (out += chunk))
    py.stderr.on('data', (chunk) => console.error('pyerr:', chunk.toString()))

    py.on('close', (code) => {
      if (code !== 0) return reject(new Error(`Python exit ${code}`))
      resolve(out.trim())
    })
  })
})