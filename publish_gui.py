#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os


class BlogPublisherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("博客发布助手")
        self.root.geometry("600x500")

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 标题
        tk.Label(self.root, text="博客文章发布助手", font=("Arial", 16)).pack(pady=10)

        # 文件选择区域
        frame_file = tk.Frame(self.root)
        frame_file.pack(pady=10, padx=20, fill="x")

        tk.Label(frame_file, text="Markdown文件:").pack(side="left")
        self.file_path = tk.StringVar()
        tk.Entry(frame_file, textvariable=self.file_path, width=50).pack(side="left", padx=5)
        tk.Button(frame_file, text="浏览...", command=self.browse_file).pack(side="left")

        # 文章预览区域
        tk.Label(self.root, text="文章预览").pack(pady=(20, 5))
        self.preview_text = scrolledtext.ScrolledText(self.root, height=15, width=70)
        self.preview_text.pack(padx=20, fill="both", expand=True)

        # 按钮区域
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=20)

        tk.Button(frame_buttons, text="加载并预览", command=self.load_preview,
                  bg="#4CAF50", fg="white").pack(side="left", padx=5)
        tk.Button(frame_buttons, text="发布文章", command=self.publish_post,
                  bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(frame_buttons, text="打开模板", command=self.open_template,
                  bg="#FF9800", fg="white").pack(side="left", padx=5)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
                 anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="选择Markdown文件",
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.load_preview()

    def load_preview(self):
        filepath = self.file_path.get()
        if not os.path.exists(filepath):
            messagebox.showerror("错误", "文件不存在！")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取标题用于预览
                lines = content.split('\n')
                title = "无标题"
                for line in lines[:10]:  # 只检查前10行
                    if line.startswith('title:'):
                        title = line.split(':', 1)[1].strip()
                        break

                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, f"标题: {title}\n\n")
                self.preview_text.insert(tk.END, content[:500] + ("..." if len(content) > 500 else ""))
                self.status_var.set(f"已加载: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {e}")

    def publish_post(self):
        filepath = self.file_path.get()
        if not filepath:
            messagebox.showerror("错误", "请先选择Markdown文件！")
            return

        # 确认对话框
        if not messagebox.askyesno("确认", "确定要发布这篇文章吗？"):
            return

        self.status_var.set("正在发布...")
        self.root.update()

        try:
            # 调用原有的发布脚本
            cmd = ["python", "publish.py", filepath, "--push"]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

            if result.returncode == 0:
                messagebox.showinfo("成功", "文章发布成功！")
                self.status_var.set("发布成功")
                # 清空当前文件路径
                self.file_path.set("")
                self.preview_text.delete(1.0, tk.END)
            else:
                messagebox.showerror("发布失败", f"错误信息:\n{result.stderr}")
                self.status_var.set("发布失败")

        except Exception as e:
            messagebox.showerror("错误", f"发布过程异常: {e}")
            self.status_var.set("错误")

    def open_template(self):
        # 打开模板文件或创建新文件
        template_path = "template.md"
        if not os.path.exists(template_path):
            # 创建基本模板
            basic_template = """---
title: 新文章标题
date: 2024年1月1日
readTime: 3分钟阅读
mood: 平静
tags: [随笔]
summary: 这里是文章摘要。
---

从这里开始写文章正文...

## 二级标题

正文内容...

![图片描述](https://example.com/image.jpg)
"""
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(basic_template)

        # 在默认编辑器中打开
        try:
            if os.name == 'nt':  # Windows
                os.startfile(template_path)
            else:  # macOS/Linux
                subprocess.run(['open', template_path] if os.name == 'posix'
                               else ['xdg-open', template_path])
        except:
            messagebox.showinfo("模板", f"模板文件: {template_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BlogPublisherGUI(root)
    root.mainloop()