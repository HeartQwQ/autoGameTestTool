// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::path::PathBuf;
use std::process::Command;
use tauri::{Manager, Runtime};

#[tauri::command]
async fn process_video<R: Runtime>(
    app: tauri::AppHandle<R>,
    video_path: String,
) -> Result<String, String> {
    // 1. 获取 Python 脚本路径
    let resource_dir = app
        .path()
        .resource_dir()
        .map_err(|e| format!("Failed to get resource dir: {}", e))?;

    let python_exe = resource_dir.join("python").join("pythonw.exe");
    let script_path = resource_dir.join("src-python").join("video_processor.py");

    // 安全检查
    if !python_exe.exists() {
        return Err(format!("Python executable not found: {:?}", python_exe));
    }
    if !script_path.exists() {
        return Err(format!("Script not found: {:?}", script_path));
    }

    // 2. 验证视频文件是否存在
    if !PathBuf::from(&video_path).exists() {
        return Err("Selected video file does not exist".to_string());
    }

    // 3. 执行 Python 脚本（无黑窗），传入视频路径
    let output = Command::new(python_exe)
        .arg(script_path)
        .arg(video_path) // 作为命令行参数传给 Python
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        let stdout = String::from_utf8(output.stdout).map_err(|e| e.to_string())?;
        Ok(stdout.trim().to_string())
    } else {
        let stderr = String::from_utf8(output.stderr).map_err(|e| e.to_string())?;
        Err(format!("Python script failed: {}", stderr))
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![process_video])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
