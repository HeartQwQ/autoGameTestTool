# pages/settings_page.py
# 本文件实现了一个设置页面，用于配置PaddlePaddle安装和推理设备
# 该页面包含置信度阈值设置、推理设备选择和PaddlePaddle安装功能

# 导入必要的模块
import subprocess  # 用于执行系统命令
import sys  # 用于访问Python系统参数
import re  # 用于正则表达式匹配
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel  # Qt基本组件
from PySide6.QtCore import Qt, QProcess  # Qt核心功能和进程管理
from qfluentwidgets import (  # QFluentWidgets组件库
    LineEdit,  # 单行输入框
    ComboBox,  # 下拉选择框
    PrimaryPushButton,  # 主要按钮
    SettingCard,  # 设置卡片
    FluentIcon as FIF,  # Fluent图标
    InfoBar,  # 信息提示栏
    InfoBarPosition,  # 信息提示位置
    MessageBox,  # 消息框
    BodyLabel  # 正文标签
)

# === 飞桨官方安装命令 ===
# 定义CPU版本安装命令
PADDLE_CPU_COMMAND = "python -m pip install paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/"
# 定义GPU版本安装命令字典，支持不同CUDA版本
PADDLE_GPU_COMMANDS = {
    "11.8": "python -m pip install paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/",
    "12.6": "python -m pip install paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/",
    "12.9": "python -m pip install paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu129/"
}
# 默认CUDA版本
DEFAULT_CUDA = "11.8"

# 设置页面类，继承自QWidget
class SettingsPage(QWidget):
    def __init__(self, parent=None):
        # 调用父类构造函数
        super().__init__(parent)
        # 设置对象名称，用于样式表识别
        self.setObjectName("settingsPage")
        # 初始化GPU可用性标志
        self.gpu_name = None
        self.cuda_ver = None
        # 初始化Paddle安装信息
        self.paddle_installed_info = None  # {"name": "...", "version": "...", "device": "CPU/GPU"}
        # 初始化Paddle安装进程
        self.paddle_process = None

        # 设置UI
        self.setup_ui()
        # 检测NVIDIA GPU
        self.detect_nvidia_gpu()
        # 检查Paddle是否已安装
        self.check_paddle_installed()
        # 初始化设备选择器
        self.init_device_selector()
        # 更新状态标签
        self.update_status_label()

    # 检测NVIDIA GPU是否可用
    def detect_nvidia_gpu(self):
        try:
            out = subprocess.check_output(["nvidia-smi"], text=True, timeout=5)
            gpu = re.search(r"NVIDIA GeForce RTX ([\w\s]+?)\s+", out)
            gpu_name = gpu.group(1).strip() if gpu else None
            cuda = re.search(r"CUDA Version:\s+(\d+\.\d+)", out)
            cuda_ver = cuda.group(1) if cuda else None

            print(f"GPU: {gpu_name} CUDA 版本: {cuda_ver}")
            self.gpu_name = gpu_name
            self.cuda_ver = cuda_ver
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            print("NVIDIA GPU not found or nvidia-smi not available")

    # 检查Paddle是否已安装
    def check_paddle_installed(self):
        """检查是否已安装 paddlepaddle 或 paddlepaddle-gpu，并尝试获取设备信息"""
        try:
            # 使用pip show命令获取包信息
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "paddlepaddle", "paddlepaddle-gpu"],
                stdout=subprocess.PIPE,  # 标准输出重定向
                stderr=subprocess.PIPE,  # 错误输出重定向
                text=True  # 文本模式
            )
            output = result.stdout  # 获取标准输出
            # 如果输出包含Name字段，则提取包名和版本
            if "Name:" in output:
                name = re.search(r"Name:\s*(.+)", output)  # 正则匹配包名
                version = re.search(r"Version:\s*(.+)", output)  # 正则匹配版本
                name = name.group(1).strip() if name else "unknown"  # 提取包名
                version = version.group(1).strip() if version else "unknown"  # 提取版本

                # 尝试导入Paddle判断设备（可选，失败则默认CPU）
                device = "CPU"
                try:
                    import paddle  # 尝试导入paddle
                    # 检查是否编译了CUDA支持
                    if paddle.is_compiled_with_cuda() and 'gpu' in paddle.get_device():
                        device = "GPU"
                except:
                    pass

                # 保存安装信息
                self.paddle_installed_info = {
                    "name": name,
                    "version": version,
                    "device": device
                }
            else:
                # 未找到安装包信息
                self.paddle_installed_info = None
        except Exception:
            # 发生异常时，设置为未安装
            self.paddle_installed_info = None

    # 设置UI界面
    def setup_ui(self):
        # 创建垂直布局
        layout = QVBoxLayout(self)
        # 设置对齐方式、边距和间距
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # === 置信度 ===
        # 创建置信度阈值设置卡片
        self.conf_card = SettingCard(
            icon=FIF.ALIGNMENT,  # 图标
            title="置信度阈值",  # 标题
            content="识别结果的最低置信度（0.0 ~ 1.0）"  # 内容描述
        )
        # 创建置信度输入框
        self.conf_input = LineEdit(self)
        self.conf_input.setPlaceholderText("例如：0.7")  # 占位文本
        self.conf_input.setText("0.7")  # 默认值
        self.conf_input.setFixedWidth(120)  # 固定宽度
        self.conf_input.setFixedHeight(33)  # 固定高度
        self.conf_input.setContentsMargins(0, 0, 20, 0)  # 内边距
        # 将输入框添加到卡片布局
        self.conf_card.hBoxLayout.addWidget(self.conf_input)

        # === 推理设备 ===
        # 创建推理设备设置卡片
        self.device_card = SettingCard(
            icon=FIF.INFO,  # 图标
            title="推理设备",  # 标题
            content="选择 CPU 或 GPU"  # 内容描述
        )
        # 创建水平布局
        device_layout = QHBoxLayout()
        device_layout.setContentsMargins(0, 0, 20, 0)  # 内边距
        device_layout.setSpacing(8)  # 间距
        # 创建设备选择下拉框
        self.device_combo = ComboBox(self)
        self.device_combo.setFixedWidth(120)  # 固定宽度
        self.device_combo.setFixedHeight(33)  # 固定高度
        # 创建安装按钮
        self.install_btn = PrimaryPushButton("安装", self)
        self.install_btn.setFixedHeight(33)  # 固定高度
        self.install_btn.setFixedWidth(80)  # 固定宽度
        # 将设备选择框和安装按钮添加到布局
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(self.install_btn)
        device_layout.addStretch()  # 添加伸缩空间
        # 将布局添加到卡片
        self.device_card.hBoxLayout.addLayout(device_layout)
        self.device_card.setContentsMargins(0, 0, 20, 0)  # 卡片边距

        # === CUDA 版本（仅 GPU 时显示）===
        # 创建CUDA版本设置卡片
        self.cuda_card = SettingCard(
            icon=FIF.BOOK_SHELF,  # 图标
            title="CUDA 版本",  # 标题
            content="请选择与你的驱动兼容的 CUDA 版本"  # 内容描述
        )
        # 创建水平布局
        cuda_layout = QHBoxLayout()
        cuda_layout.setContentsMargins(0, 0, 20, 0)  # 内边距
        cuda_layout.setSpacing(8)  # 间距
        # 创建CUDA版本选择下拉框
        self.cuda_combo = ComboBox(self)
        self.cuda_combo.addItems(["11.8", "12.6", "12.9"])  # 添加选项
        self.cuda_combo.setCurrentText(DEFAULT_CUDA)  # 设置默认值
        self.cuda_combo.setFixedWidth(120)  # 固定宽度
        self.cuda_combo.setFixedHeight(33)  # 固定高度
        # 将下拉框添加到布局
        cuda_layout.addWidget(self.cuda_combo)
        cuda_layout.addStretch()  # 添加伸缩空间
        # 将布局添加到卡片
        self.cuda_card.hBoxLayout.addLayout(cuda_layout)
        self.cuda_card.setContentsMargins(0, 0, 20, 0)  # 卡片边距

        # === 当前状态 ===
        # 创建当前状态设置卡片
        self.status_card = SettingCard(
            icon=FIF.INFO,  # 图标
            title="当前状态",  # 标题
            content="安装版本"  # 内容
        )
        # 创建状态标签
        self.status_label = BodyLabel("安装版本", self)
        self.status_label.setContentsMargins(0, 0, 20, 0)  # 内边距
        # 将标签添加到卡片
        self.status_card.hBoxLayout.addWidget(self.status_label)

        # 将所有卡片添加到主布局
        layout.addWidget(self.conf_card)
        layout.addWidget(self.device_card)
        layout.addWidget(self.cuda_card)
        layout.addWidget(self.status_card)
        layout.addStretch()  # 添加伸缩空间

    # 初始化设备选择器
    def init_device_selector(self):
        # 创建设备列表
        devices = ["CPU"]
        # 如果GPU可用，添加GPU选项
        if self.gpu_available:
            devices.append("GPU")

        # 将设备选项添加到下拉框
        self.device_combo.addItems(devices)
        # 设置默认选择（如果没有GPU则CPU，否则GPU）
        self.device_combo.setCurrentIndex(0 if not self.gpu_available else 1)
        # 连接设备变化信号
        self.device_combo.currentTextChanged.connect(self.on_device_changed)
        # 初始显示
        self.on_device_changed(self.device_combo.currentText())  # 初始化显示

        # 连接安装按钮点击事件
        self.install_btn.clicked.connect(self.on_install_clicked)

    # 设备变化处理
    def on_device_changed(self, text):
        # 如果选择的是GPU，则显示CUDA版本选择
        self.cuda_card.setVisible(text == "GPU")

    # 更新状态标签
    def update_status_label(self):
        # 根据安装信息更新状态标签
        if self.paddle_installed_info:
            info = self.paddle_installed_info
            text = f"✅ 已安装：{info['name']} {info['version']} ({info['device']})"
        else:
            text = "❌ 未检测到 PaddlePaddle"
        self.status_label.setText(text)

    # 获取安装命令
    def get_install_command(self):
        # 获取当前选择的设备
        device = self.device_combo.currentText()
        if device == "GPU":
            # 获取CUDA版本
            cuda_ver = self.cuda_combo.currentText()
            # 返回对应的安装命令
            return PADDLE_GPU_COMMANDS.get(cuda_ver, PADDLE_GPU_COMMANDS[DEFAULT_CUDA])
        else:
            # 返回CPU安装命令
            return PADDLE_CPU_COMMAND

    # 安装按钮点击处理
    def on_install_clicked(self):
        # 如果已安装Paddle，提示用户确认
        if self.paddle_installed_info:
            msg_box = MessageBox(
                title="确认切换版本",
                content="检测到已安装 PaddlePaddle。\n是否卸载当前版本并安装新版本？",
                parent=self
            )
            if not msg_box.exec():
                return

        # 获取安装命令
        raw_cmd = self.get_install_command()
        cmd = raw_cmd.split()  # 将命令分割为列表

        # 调试输出
        print(" 执行命令:", raw_cmd)

        # 禁用安装按钮，显示"安装中..."
        self.install_btn.setEnabled(False)
        self.install_btn.setText("安装中...")

        # 创建进程
        self.paddle_process = QProcess(self)
        # 设置进程程序和参数
        self.paddle_process.setProgram(cmd[0])
        self.paddle_process.setArguments(cmd[1:])

        # 连接输出和错误信号
        self.paddle_process.readyReadStandardOutput.connect(self.on_stdout)
        self.paddle_process.readyReadStandardError.connect(self.on_stderr)
        self.paddle_process.errorOccurred.connect(self.on_process_error)
        self.paddle_process.finished.connect(self.on_install_finished)

        # 启动进程
        self.paddle_process.start()

        # 显示安装开始信息
        InfoBar.info(
            title="开始安装",
            content="正在安装 PaddlePaddle，请稍候...",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=4000,
            parent=self
        )

    # 标准输出处理
    def on_stdout(self):
        # 读取标准输出
        output = self.paddle_process.readAllStandardOutput().data().decode(errors='ignore')
        # 打印调试信息
        print(" STDOUT:", output.strip())

    # 标准错误处理
    def on_stderr(self):
        # 读取标准错误
        error = self.paddle_process.readAllStandardError().data().decode(errors='ignore')
        # 打印调试信息
        print("⚠️ STDERR:", error.strip())

    # 进程错误处理
    def on_process_error(self, error):
        # 打印进程错误
        print(" QProcess 错误:", error, self.paddle_process.errorString())

    # 安装完成处理
    def on_install_finished(self, exit_code, exit_status):
        # 启用安装按钮
        self.install_btn.setEnabled(True)
        # 根据是否已安装设置按钮文本
        if self.paddle_installed_info:
            self.install_btn.setText("重新安装")
        else:
            self.install_btn.setText("安装")

        # 检查安装是否成功
        if exit_code == 0:
            # 成功后重新检测状态
            self.check_paddle_installed()
            self.update_status_label()
            # 显示成功信息
            InfoBar.success(
                title="安装成功",
                content="PaddlePaddle 已更新！请重启应用以生效。",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=6000,
                parent=self
            )
        else:
            # 显示错误信息
            InfoBar.error(
                title="安装失败",
                content="请检查网络或手动运行安装命令。",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=8000,
                parent=self
            )

    # 获取配置
    def get_config(self):
        # 获取置信度阈值
        try:
            conf = float(self.conf_input.text())
            # 验证置信度范围
            if not (0.0 <= conf <= 1.0):
                conf = 0.7
        except ValueError:
            conf = 0.7

        # 获取设备和CUDA版本
        device = self.device_combo.currentText()
        cuda = self.cuda_combo.currentText() if device == "GPU" else None
        # 返回配置字典
        return {
            "confidence": conf,
            "device": device,
            "cuda_version": cuda,
        }