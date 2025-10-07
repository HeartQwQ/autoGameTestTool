from pathlib import Path

import json
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext
import pandas as pd
from io import StringIO

def convert_to_json():
    raw_text = text_input.get("1.0", tk.END).strip()
    if not raw_text:
        messagebox.showwarning("输入为空", "请先粘贴表格内容！")
        return

    try:
        # 用制表符分隔读取为表格
        df = pd.read_csv(StringIO(raw_text), sep='\t')
        json_data = df.to_dict(orient='records')

        # 获取桌面路径
        output_path = os.path.join(Path("../json"), "数值表.json")

        # 写入 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("成功", f"JSON 文件已生成：\n{output_path}")
    except Exception as e:
        messagebox.showerror("转换失败", f"错误信息：\n{str(e)}")

# 创建窗口
root = tk.Tk()
root.title("表格转 JSON 工具")
root.geometry("500x400")

# 输入框
tk.Label(root, text="请粘贴表格内容（制表符分隔）：").pack(pady=5)
text_input = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
text_input.pack(fill=tk.BOTH, padx=10, pady=5)

# 转换按钮
convert_btn = tk.Button(root, text="转换为 JSON 并保存到当前目录json文件夹下", command=convert_to_json)
convert_btn.pack(pady=10)

# 启动主循环
root.mainloop()