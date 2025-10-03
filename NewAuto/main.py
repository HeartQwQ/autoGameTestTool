# main.py
import sys
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition,
    FluentIcon as FIF, setTheme, Theme
)
from pages.video_page import VideoProcessPage
from pages.settings_page import SettingsPage  # ← 新增导入


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自动化测试工具")
        self.resize(960, 720)

        # 创建页面
        self.video_page = VideoProcessPage(self)
        self.settings_page = SettingsPage(self)  # ← 新增

        # 添加导航
        self.addSubInterface(
            interface=self.video_page,
            icon=FIF.VIDEO,
            text="视频处理",
            position=NavigationItemPosition.TOP
        )
        self.addSubInterface(
            interface=self.settings_page,
            icon=FIF.SETTING,
            text="设置",
            position=NavigationItemPosition.BOTTOM  # 放到底部
        )

        self.setMicaEffectEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    setTheme(Theme.LIGHT)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())