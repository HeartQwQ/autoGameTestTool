# pages/video_page.py
import os

from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    BodyLabel, PrimaryPushButton, FluentIcon as FIF
)


class VideoProcessPage(QWidget):
    """视频处理页面，支持按钮上传和拖拽上传"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("videoProcessPage")  # ← 关键修复！
        self.setAcceptDrops(True)
        self.video_path = None

        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setSpacing(20)

        # 提示标签
        self.tip_label = BodyLabel("将视频文件拖拽到此处，或点击下方按钮上传", self)
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tip_label.setWordWrap(True)

        # 上传按钮
        self.upload_btn = PrimaryPushButton("📁 上传视频", self)
        self.upload_btn.setIcon(FIF.VIDEO)
        self.upload_btn.clicked.connect(self.select_video)

        # 按钮布局居中
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addStretch()

        # 添加到主布局
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.tip_label)
        self.main_layout.addLayout(btn_layout)
        self.main_layout.addStretch()

        # 设置样式（可选：添加虚线边框模拟拖拽区）
        self.setStyleSheet("""
            VideoProcessPage {
                border: 2px dashed rgba(0, 120, 215, 0.3);
                border-radius: 12px;
                background-color: rgba(240, 248, 255, 0.4);
            }
        """)

    def select_video(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.flv *.wmv)"
        )
        if path:
            self.set_video_path(path)

    def set_video_path(self, path: str):
        self.video_path = path
        filename = os.path.basename(path)
        self.tip_label.setText(f"✅ 已加载视频：\n{filename}")
        self.tip_label.setStyleSheet("color: #0078D4; font-weight: bold;")

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime: QMimeData = event.mimeData()
        if mime.hasUrls() and len(mime.urls()) == 1:
            url = mime.urls()[0]
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')):
                    event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        url = event.mimeData().urls()[0]
        file_path = url.toLocalFile()
        self.set_video_path(file_path)

    def get_video_path(self):
        """供外部调用获取当前视频路径"""
        return self.video_path