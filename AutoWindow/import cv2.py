import cv2
import os
import numpy as np
from pathlib import Path
import argparse

class VideoToFrames:
    def __init__(self, video_path, output_dir="frames"):
        """
        视频转帧工具
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
        """
        self.video_path = r'C:\Users\dpdai\Desktop\3456789.mp4'
        self.output_dir = r'C:\Users\dpdai\Desktop\frames'
        
        # 创建输出目录
        Path(self.output_dir).mkdir(exist_ok=True)
    
    def extract_frames(self, frame_interval=1, image_format='jpg'):
        """
        提取视频帧并保存为图片
        
        Args:
            frame_interval: 帧间隔，1表示每帧都保存，2表示每隔一帧保存
            image_format: 图片格式 ('jpg', 'png', 'bmp')
        """
        # 打开视频文件
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            print(f"错误：无法打开视频文件 {self.video_path}")
            return False
        
        # 获取视频信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps
        
        print(f"视频信息：")
        print(f"  总帧数: {total_frames}")
        print(f"  帧率: {fps:.2f} FPS")
        print(f"  时长: {duration:.2f} 秒")
        print(f"  输出目录: {self.output_dir}")
        print(f"  帧间隔: {frame_interval}")
        print(f"  图片格式: {image_format}")
        print("-" * 50)
        
        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # 根据帧间隔决定是否保存当前帧
            if frame_count % frame_interval == 0:
                # 生成文件名
                filename = f"frame_{frame_count:06d}.{image_format}"
                filepath = os.path.join(self.output_dir, filename)
                
                # 保存帧为图片
                success = cv2.imwrite(filepath, frame)
                
                if success:
                    saved_count += 1
                    if saved_count % 100 == 0:  # 每保存100帧显示一次进度
                        progress = (frame_count / total_frames) * 100
                        print(f"进度: {progress:.1f}% - 已保存 {saved_count} 帧")
                else:
                    print(f"警告：保存帧 {frame_count} 失败")
            
            frame_count += 1
        
        # 释放资源
        cap.release()
        
        print("-" * 50)
        print(f"提取完成！")
        print(f"  处理帧数: {frame_count}")
        print(f"  保存帧数: {saved_count}")
        print(f"  输出目录: {self.output_dir}")
        
        return True
    
    def extract_frames_by_time(self, time_interval=1.0, image_format='jpg'):
        """
        按时间间隔提取帧
        
        Args:
            time_interval: 时间间隔（秒）
            image_format: 图片格式
        """
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            print(f"错误：无法打开视频文件 {self.video_path}")
            return False
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * time_interval)
        
        print(f"按时间间隔提取帧：每 {time_interval} 秒提取一帧")
        print(f"对应帧间隔：{frame_interval} 帧")
        
        cap.release()
        
        return self.extract_frames(frame_interval, image_format)

def main():
    # 创建视频转帧工具实例
    video_path = r'C:\Users\dpdai\Desktop\123.mp4'
    output_dir = r'C:\Users\dpdai\Desktop\frames'
    converter = VideoToFrames(video_path, output_dir)
    
    # 检查视频文件是否存在
    if not os.path.exists(converter.video_path):
        print(f"错误：视频文件不存在 {converter.video_path}")
        return
    
    print("视频转帧工具")
    print("=" * 50)
    
    # 选择提取模式
    print("请选择提取模式：")
    print("1. 按帧间隔提取（每N帧提取一帧）")
    print("2. 按时间间隔提取（每N秒提取一帧）")
    print("3. 提取所有帧")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == '1':
        interval = int(input("请输入帧间隔 (默认1): ") or "1")
        converter.extract_frames(frame_interval=interval)
    elif choice == '2':
        interval = float(input("请输入时间间隔(秒) (默认1.0): ") or "1.0")
        converter.extract_frames_by_time(time_interval=interval)
    elif choice == '3':
        converter.extract_frames(frame_interval=1)
    else:
        print("无效选择，使用默认设置提取所有帧")
        converter.extract_frames(frame_interval=1)

if __name__ == "__main__":
    main()