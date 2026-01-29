#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
静态博客文章发布助手
功能：读取Markdown文件，自动生成JSON并更新索引
"""

import os
import json
import re
import sys
import datetime
from pathlib import Path
import subprocess
import argparse

# ========== 配置区域 ==========
# 请根据你的项目结构调整这些路径
POSTS_DIR = Path("./posts")  # 存放文章JSON的文件夹
INDEX_FILE = Path("./posts_index.json")  # 文章索引文件


# =============================

def parse_front_matter(content):
    """
    解析Markdown文件顶部的Front Matter（YAML格式）
    格式示例：
    ---
    title: 我的新文章
    date: 2024年5月22日
    readTime: 3分钟阅读
    mood: 开心
    tags: [生活, 随笔]
    summary: 这是一篇文章的简要摘要。
    ---
    """
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        raise ValueError("Markdown文件必须以Front Matter（以---开始）开头")

    front_matter = []
    for line in lines[1:]:
        if line.strip() == '---':
            break
        front_matter.append(line)

    # 简单解析YAML（为简化，这里不使用完整YAML解析器）
    metadata = {}
    for line in front_matter:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # 处理标签数组
            if key == 'tags':
                # 移除括号和引号，按逗号分割
                tags = value.strip('[]').split(',')
                metadata[key] = [tag.strip().strip("'\" ") for tag in tags]
            else:
                metadata[key] = value

    # 提取正文（Front Matter之后的内容）
    body_start = content.find('---\n') + 4
    if body_start == 3:  # 没找到
        body_start = content.find('---\r\n') + 5
    body = content[body_start:].strip()

    return metadata, body


def markdown_to_html(text):
    """
    将Markdown基本语法转换为HTML
    （这是一个简化版，可替换为更强大的库如markdown2）
    """
    # 处理标题
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # 处理粗体和斜体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    # 处理列表
    text = re.sub(r'^\* (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)

    # 处理代码块（简单处理）
    text = re.sub(r'```(\w+)?\n(.+?)\n```', r'<pre><code>\2</code></pre>',
                  text, flags=re.DOTALL)

    # 处理行内代码
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # 处理图片 ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',
                  r'<img src="\2" alt="\1" style="max-width:100%;">', text)

    # 处理链接 [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    # 处理换行：两个换行符转为段落
    paragraphs = text.split('\n\n')
    html_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p:
            # 如果已经是列表项，不包裹<p>
            if p.startswith('<li>') or p.startswith('<pre>') or p.startswith('<h'):
                html_paragraphs.append(p)
            else:
                html_paragraphs.append(f'<p>{p}</p>')

    return '\n'.join(html_paragraphs)


def generate_post_id(title):
    """
    根据标题生成文章ID（用于文件名）
    格式：YYYY-MM-DD-标题的英文或拼音
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    # 简单中文转拼音（此处为示意，实际可用pypinyin库）
    # 这里先用标题的英文或拼音，为简化先用数字
    import random
    random_str = str(random.randint(1000, 9999))
    # 移除特殊字符，用连字符连接
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().lower()
    safe_title = re.sub(r'[-\s]+', '-', safe_title)

    # 如果标题转换后为空，使用随机数
    if not safe_title or len(safe_title) > 50:
        safe_title = random_str

    return f"{today}-{safe_title}"


def load_json_file(filepath):
    """安全地加载JSON文件"""
    if not os.path.exists(filepath):
        return [] if 'index' in str(filepath).lower() else {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"警告：{filepath} 不是有效的JSON，将创建新文件")
        return [] if 'index' in str(filepath).lower() else {}


def save_json_file(data, filepath):
    """保存JSON文件（带格式化）"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='静态博客文章发布助手')
    parser.add_argument('file', help='Markdown源文件路径')
    parser.add_argument('--push', '-p', action='store_true',
                        help='自动推送到GitHub仓库')
    parser.add_argument('--no-push', '-n', action='store_true',
                        help='只更新本地文件，不推送')

    args = parser.parse_args()

    print("=" * 50)
    print("静态博客发布助手")
    print("=" * 50)

    # 1. 读取Markdown文件
    md_file = Path(args.file)
    if not md_file.exists():
        print(f"错误：文件 '{md_file}' 不存在")
        sys.exit(1)

    print(f"📖 正在处理文件: {md_file.name}")

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)

    # 2. 解析Front Matter
    try:
        metadata, body = parse_front_matter(content)
    except Exception as e:
        print(f"解析Front Matter失败: {e}")
        print("请确保文件以正确的Front Matter格式开头（前后有---）")
        sys.exit(1)

    # 检查必要字段
    required_fields = ['title', 'summary']
    for field in required_fields:
        if field not in metadata:
            print(f"错误：Front Matter中缺少必要字段 '{field}'")
            sys.exit(1)

    # 设置默认值
    if 'date' not in metadata:
        today_cn = datetime.date.today().strftime("%Y年%-m月%-d日")
        metadata['date'] = today_cn

    if 'readTime' not in metadata:
        metadata['readTime'] = "3分钟阅读"

    if 'mood' not in metadata:
        metadata['mood'] = "平静"

    if 'tags' not in metadata:
        metadata['tags'] = ["随笔"]

    print(f"✅ 解析成功: 《{metadata['title']}》")

    # 3. 转换Markdown为HTML
    html_body = markdown_to_html(body)
    print("✅ Markdown已转换为HTML")

    # 4. 生成文章ID和文件名
    post_id = generate_post_id(metadata['title'])
    json_filename = f"{post_id}.json"
    json_path = POSTS_DIR / json_filename

    # 确保posts目录存在
    POSTS_DIR.mkdir(exist_ok=True)

    # 5. 创建文章详情JSON
    post_detail = {
        "id": post_id,
        "title": metadata['title'],
        "date": metadata['date'],
        "readTime": metadata['readTime'],
        "mood": metadata['mood'],
        "tags": metadata['tags'],
        "summary": metadata['summary'],
        "body": html_body
    }

    save_json_file(post_detail, json_path)
    print(f"📄 文章详情已保存: {json_path}")

    # 6. 更新文章索引
    index_data = load_json_file(INDEX_FILE)

    # 创建索引条目（不包含body）
    index_entry = {k: v for k, v in post_detail.items() if k != 'body'}

    # 添加到索引开头（最新文章在前）
    index_data.insert(0, index_entry)

    save_json_file(index_data, INDEX_FILE)
    print(f"📚 文章索引已更新: {INDEX_FILE}")

    print("\n" + "=" * 50)
    print("✅ 文章发布成功！")
    print(f"文章ID: {post_id}")
    print(f"标题: {metadata['title']}")
    print(f"日期: {metadata['date']}")
    print(f"标签: {', '.join(metadata['tags'])}")
    print("=" * 50)

    # 7. 可选：推送到GitHub
    should_push = args.push
    if args.no_push:
        should_push = False
    elif not args.push and not args.no_push:
        # 如果没有指定参数，询问用户
        try:
            response = input("\n是否要推送更新到GitHub仓库？(y/N): ").strip().lower()
            should_push = response == 'y'
        except KeyboardInterrupt:
            should_push = False
            print("\n操作已取消")

    if should_push:
        print("\n🚀 正在推送到GitHub...")
        try:
            # 添加文件
            subprocess.run(['git', 'add', str(json_path), str(INDEX_FILE)],
                           check=True, capture_output=True, text=True)

            # 提交
            commit_msg = f"发布新文章: {metadata['title']}"
            subprocess.run(['git', 'commit', '-m', commit_msg],
                           check=True, capture_output=True, text=True)

            # 推送
            result = subprocess.run(['git', 'push'],
                                    capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ 已成功推送到GitHub！")
                print("📢 等待约1-2分钟，GitHub Pages会自动部署更新。")
                print(f"🌐 访问: https://你的用户名.github.io")
            else:
                print("⚠️  推送失败，请检查Git配置:")
                print(result.stderr)

        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
            print("请确保：")
            print("1. 当前目录是Git仓库")
            print("2. Git已正确配置")
            print("3. 你有推送权限")
        except FileNotFoundError:
            print("❌ Git未安装或不在PATH中")
    else:
        print("\n📝 本地文件已更新完成。")
        print("你可以稍后手动执行以下命令推送到GitHub：")
        print(f"  git add {json_path} {INDEX_FILE}")
        print(f'  git commit -m "发布新文章: {metadata["title"]}"')
        print("  git push")


if __name__ == '__main__':
    main()