import time
import numpy as np
import cv2
import ctypes
from ctypes import windll, wintypes
import win32api
import win32gui
import win32ui
import win32con
from pathlib import Path
from PIL import Image, ImageDraw
from typing import Optional, Tuple, Dict, Any, Union
import pyautogui
from pyautogui import _pyautogui_win as platformModule   # 仅 Windows


# 设置 DPI 感知（重要！）
windll.user32.SetProcessDPIAware()


# # 告诉 pyautogui 用“物理像素”而不是“逻辑像素”
# platformModule.DPI_SCALE = 1.0
# pyautogui.FAILSAFE = False   # 先关掉，排除干扰
# pyautogui.PAUSE = 0.05             # 每一步默认暂停 50 ms，防止丢事件
# # 高 DPI 自动适配（需要 pyautogui 0.9.41 及以上）
# pyautogui.useImageNotFoundException(False)


# -------------- 公开接口 --------------
def capture_window(
        hwnd,
        save_path: Optional[Union[str, Path]] = None
) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    对指定标题的窗口进行客户区截图
    :param hwnd: 窗口句柄
    :param save_path: 保存路径（str 或 Path，None 表示不落盘）
    :return: (PIL 图像, 信息字典)
    """
    # 2. 获取窗口整体/客户区矩形
    x, y, w, h = win32gui.GetWindowRect(hwnd)  # 屏幕坐标，含边框
    cx, cy, cw, ch = win32gui.GetClientRect(hwnd)  # 客户区坐标，相对窗口
    # print('窗口矩形:', win32gui.GetWindowRect(hwnd))
    # print('客户矩形:', win32gui.GetClientRect(hwnd))

    # 3. 计算客户区在屏幕上的实际左上角
    border = (w - x - cw) // 2  # 左右边框宽度
    title_h = (h - y - ch) - border  # 标题栏+下边框
    cx_screen = x + border  # 客户区屏幕 x
    cy_screen = y + title_h  # 客户区屏幕 y

    # 获取窗口设备上下文
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # 创建位图
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, cw, ch)
    saveDC.SelectObject(saveBitMap)

    # 使用 BitBlt 截图
    saveDC.BitBlt((-border, -title_h), (cw + border, ch + title_h), mfcDC, (0, 0), win32con.SRCCOPY)

    # 转换为 PIL 图像
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )

    # 7. 可选是否保存为图片
    if save_path:
        img.save(save_path)

    # 清理资源
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    # 9. 组装返回信息
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    info_window = {
        "hwnd": hwnd,
        "window_rect": (x, y, w, h),  # (left, top, right, bottom)
        "client_size": (cw, ch),  # (width, height)
        "client_screen_pos": (cx_screen, cy_screen),
        "save_path": save_path
    }
    return img_cv, info_window


# -------------- 内部辅助 -------------
def find_window(title):
    """根据窗口标题查找窗口句柄"""
    def enum_callback(hwnd, window):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            window.append(hwnd)

    windows = []
    win32gui.EnumWindows(enum_callback, windows)
    win32gui.SetForegroundWindow(windows[0])
    # left, top, width, height = pyautogui.getWindowsWithTitle(title)[0].box
    # cx, cy = left + width // 2, top + 15  # 标题栏中心
    # pyautogui.click(cx, cy, _pause=False)  # 激活
    time.sleep(0.2)
    return windows[0] if windows else None


def text_center(box: list, poi_img, log_dir) -> tuple:
    """矩形框 [x1,y1,x2,y2] → 绝对中心 (cx,cy)"""
    x1, y1, x2, y2 = box
    cv2.rectangle(poi_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.imencode(".png", poi_img)[1].tofile(log_dir)

    return (x1 + x2) // 2, (y1 + y2) // 2


def mouse_click(cx: int, cy: int):
    """绝对坐标单击"""
    win32api.SetCursorPos((cx, cy))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def snap_center_rect(cx_screen: int, cy_screen: int,
                     w: int = 51, h: int = 51,
                     save_path: Path | str = "center_snap.png") -> Tuple[Image.Image, str]:
    """
    以 (cx_screen, cy_screen) 为中心，截w,h宽高矩形，
    并在中心画红色圆点，保存并返回小图。
    """
    # 计算左上角
    left = cx_screen - w // 2
    top = cy_screen - h // 2

    # 1. 屏幕拷贝
    hdc_screen = win32gui.GetDC(0)
    hdc_mem = win32gui.CreateCompatibleDC(hdc_screen)
    hbmp = win32gui.CreateCompatibleBitmap(hdc_screen, w, h)
    hbmp_old = win32gui.SelectObject(hdc_mem, hbmp)
    win32gui.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, left, top, win32con.SRCCOPY)

    # 2. 位图 → PIL
    bmp = win32ui.CreateBitmapFromHandle(hbmp)
    img = Image.frombuffer("RGB", (w, h), bmp.GetBitmapBits(True),
                           "raw", "BGRX", 0, 1)

    # 3. 画中心红点（半径 2 px）
    draw = ImageDraw.Draw(img)
    center = (w // 2, h // 2)
    r = 2
    draw.ellipse([(center[0] - r, center[1] - r),
                  (center[0] + r, center[1] + r)], fill="red")

    # 4. 清理 GDI
    win32gui.SelectObject(hdc_mem, hbmp_old)
    win32gui.DeleteObject(hbmp)
    win32gui.DeleteDC(hdc_mem)
    win32gui.ReleaseDC(0, hdc_screen)

    save_path = Path(save_path)
    img.save(save_path)
    return img, str(save_path)


def tap(vk: str):
    """按一下虚拟键码"""
    key = None
    if vk == "ESC":
        key = win32con.VK_ESCAPE
    elif vk == "空格":
        key = win32con.VK_SPACE
    else:
        print(f"无法识别的指令：{vk}")
        return False

    win32api.keybd_event(key, 0, 0, 0)  # 按下
    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)  # 松开
    print(f"已执行按下{vk}并抬起，虚拟码{key}")

    return True


def slide_from(x_start: int, y_start: int,
               direction: str,
               distance: int = 200,
               duration: float = 0.5):
    """
    从指定方向滑入终点坐标
    direction ∈ {'上','下','左','右'}
    distance  : 滑动距离（像素）
    duration  : 滑动耗时（秒）
    """
    # 激活窗口
    find_window("和平精英模拟器高清版")

    # 1. 计算移动后的坐标
    x_end, y_end = x_start, y_start
    if "左" in direction:
        x_end = x_start - distance
    elif "右" in direction:
        x_end = x_start + distance
    elif "上" in direction:
        y_end = y_start + distance
    elif "下" in direction:
        y_end = y_start + distance

    print(x_start, y_start, x_end, y_end)
    time.sleep(1)

    pyautogui.moveTo(x_start, y_start, tween=pyautogui.linear, _pause=False)
    time.sleep(0.1)



# slide_from(6820, 480, "下", 300)

# mouse_click(6820, 480)