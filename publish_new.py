#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互式博客文章发布助手
直接在终端中引导输入，一键发布
"""

import os
import json
import datetime
import sys
from pathlib import Path
import subprocess

# ========== 配置 ==========
POSTS_DIR = Path("./posts")
INDEX_FILE = Path("./posts_index.json")


# ==========================

def ask_question(question, default="", required=True):
    """友好的提问函数"""
    while True:
        if default:
            prompt = f"{question} [{default}]: "
        else:
            prompt = f"{question}: "

        answer = input(prompt).strip()

        if not answer:
            if default:
                return default
            elif not required:
                return ""
            else:
                print("⚠️  此项不能为空，请重新输入")
                continue
        return answer


def generate_post_id(title):
    """生成文章ID"""
    today = datetime.date.today().strftime("%Y-%m-%d")

    # 简单处理中文标题：转为拼音或使用日期+序号
    import re
    import random

    # 移除所有非字母数字字符，用连字符连接
    title_slug = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', title)  # 保留中文
    title_slug = re.sub(r'[-\s]+', '-', title_slug)
    title_slug = title_slug.lower()

    # 如果转换后为空或太长，使用日期和随机数
    if not title_slug or len(title_slug) > 50:
        title_slug = f"post-{random.randint(1000, 9999)}"

    return f"{today}-{title_slug}"


def edit_content_interactively():
    """交互式编辑文章正文"""
    print("\n" + "=" * 50)
    print("📝 编辑文章正文（输入完所有内容后，在新的一行输入'END'结束）")
    print("=" * 50)
    print("提示：")
    print("  • 直接输入文字即可")
    print("  • 如需换行，直接按回车")
    print("  • 输入完成后，在新的一行输入 END")
    print("  • 支持简单的HTML标签，如 <strong>粗体</strong>")
    print("-" * 50)

    lines = []
    line_num = 1

    while True:
        try:
            line = input(f"[{line_num}] ").rstrip('\n')
            if line.upper() == "END":
                break
            lines.append(line)
            line_num += 1
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n⚠️  编辑中断")
            return None

    return '\n'.join(lines)


def ask_tags():
    """询问标签"""
    print("\n🏷️  请输入文章标签（用逗号或空格分隔，直接回车跳过）")
    tags_input = input("标签: ").strip()

    if not tags_input:
        return ["随笔"]

    # 支持逗号或空格分隔
    if ',' in tags_input:
        tags = [tag.strip() for tag in tags_input.split(',')]
    else:
        tags = [tag.strip() for tag in tags_input.split()]

    # 清理标签，移除特殊字符
    import re
    clean_tags = []
    for tag in tags:
        if tag:
            clean_tag = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', tag)
            if clean_tag:
                clean_tags.append(clean_tag)

    return clean_tags[:5]  # 最多5个标签


def ask_image():
    """询问是否添加图片"""
    print("\n🖼️  是否添加图片？")
    print("1. 不添加图片")
    print("2. 从网络图片链接添加")
    print("3. 稍后手动编辑添加")

    choice = input("请选择 (1/2/3, 默认1): ").strip() or "1"

    if choice == "2":
        image_url = input("请输入图片URL: ").strip()
        if image_url:
            alt_text = input("图片描述文字: ").strip() or "文章配图"
            return f'\n<img src="{image_url}" alt="{alt_text}" style="max-width:100%;border-radius:8px;margin:1rem 0;">\n'

    return ""


def get_today_date():
    """获取今天日期（兼容Windows的格式）"""
    today = datetime.date.today()
    # Windows兼容的日期格式：去掉前导零
    month = str(today.month)
    day = str(today.day)
    return f"{today.year}年{month}月{day}日"


def create_post():
    """主函数：创建新文章"""
    print("\n" + "=" * 50)
    print("✨ 博客文章发布助手 ✨")
    print("=" * 50)

    # 1. 询问基本信息
    print("\n📌 第一步：基本信息")
    print("-" * 30)

    title = ask_question("文章标题", required=True)

    # 自动生成日期，但允许修改（使用兼容Windows的格式）
    today_cn = get_today_date()
    date = ask_question("发布日期", today_cn)

    readTime = ask_question("阅读时长", "3分钟阅读")

    # 心情选择
    print("\n😊 选择心情：")
    moods = ["开心", "平静", "思考", "兴奋", "怀念", "期待", "放松", "其他"]
    for i, mood in enumerate(moods, 1):
        print(f"  {i}. {mood}")

    mood_choice = input(f"请选择 (1-{len(moods)}, 默认1): ").strip()
    if mood_choice.isdigit() and 1 <= int(mood_choice) <= len(moods):
        mood = moods[int(mood_choice) - 1]
    else:
        mood = ask_question("自定义心情", "平静")

    summary = ask_question("文章摘要", required=True)

    # 2. 询问标签
    tags = ask_tags()

    # 3. 编辑正文
    body = edit_content_interactively()
    if body is None:
        print("❌ 文章创建取消")
        return

    # 4. 询问图片
    image_html = ask_image()
    if image_html:
        insert_pos = input("\n图片插入位置（输入行号，直接回车插入到正文末尾）: ").strip()
        if insert_pos.isdigit():
            lines = body.split('\n')
            pos = int(insert_pos) - 1
            if 0 <= pos <= len(lines):
                lines.insert(pos, image_html)
                body = '\n'.join(lines)
        else:
            body += image_html

    # 5. 生成文章ID和文件
    post_id = generate_post_id(title)
    json_filename = f"{post_id}.json"
    json_path = POSTS_DIR / json_filename

    # 确保目录存在
    POSTS_DIR.mkdir(exist_ok=True)

    # 6. 创建文章详情JSON
    post_detail = {
        "id": post_id,
        "title": title,
        "date": date,
        "readTime": readTime,
        "mood": mood,
        "tags": tags,
        "summary": summary,
        "body": body.replace('\n', '<br>')
    }

    # 7. 预览确认
    print("\n" + "=" * 50)
    print("📋 文章预览")
    print("=" * 50)
    print(f"标题：{title}")
    print(f"日期：{date}")
    print(f"标签：{', '.join(tags)}")
    print(f"摘要：{summary}")
    print(f"正文预览：{body[:100]}...")
    print(f"文件将保存为：{json_path}")
    print("=" * 50)

    confirm = input("\n是否确认发布？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 发布取消")
        return

    # 8. 保存文件
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(post_detail, f, ensure_ascii=False, indent=2)
        print(f"✅ 文章已保存: {json_path}")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return

    # 9. 更新索引
    try:
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = []

        # 创建索引条目（不包含body）
        index_entry = {k: v for k, v in post_detail.items() if k != 'body'}
        index_data.insert(0, index_entry)  # 最新文章在最前面

        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 文章索引已更新: {INDEX_FILE}")

    except Exception as e:
        print(f"⚠️  更新索引失败，需要手动更新: {e}")
        # 提供手动更新指南
        print("\n📝 请手动更新 posts_index.json，添加以下内容：")
        print(json.dumps(index_entry, ensure_ascii=False, indent=2))

    # 10. 询问是否推送到GitHub
    print("\n" + "=" * 50)
    push_choice = input("是否立即推送到GitHub？(y/N): ").strip().lower()

    if push_choice == 'y':
        push_to_github(json_path, title)
    else:
        print("\n📝 本地发布完成！")
        print("你可以稍后手动执行以下命令推送到GitHub：")
        print(f"  git add {json_path} {INDEX_FILE}")
        print(f'  git commit -m "发布新文章: {title}"')
        print("  git push")


def push_to_github(json_path, title):
    """推送到GitHub"""
    print("\n🚀 正在推送到GitHub...")
    try:
        # 添加文件
        subprocess.run(['git', 'add', str(json_path), str(INDEX_FILE)],
                       check=True, capture_output=True, text=True)

        # 提交
        commit_msg = f"发布新文章: {title}"
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
            print("⚠️  推送失败:")
            print(result.stderr[:200])  # 只显示前200字符
            print("\n💡 你可以稍后手动执行:")
            print(f"  git add {json_path} {INDEX_FILE}")
            print(f'  git commit -m "发布新文章: {title}"')
            print("  git push")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git操作失败: {e}")
        print("请确保：")
        print("1. 当前目录是Git仓库")
        print("2. Git已正确配置")
    except FileNotFoundError:
        print("❌ Git未安装或不在PATH中")
        print("你可以稍后手动推送")


def edit_existing_post():
    """编辑现有文章（简单版）"""
    print("\n📝 编辑现有文章")

    if not POSTS_DIR.exists():
        print("❌ posts目录不存在")
        return

    # 列出所有文章
    posts = list(POSTS_DIR.glob("*.json"))
    if not posts:
        print("❌ 没有找到文章")
        return

    print("\n现有文章：")
    for i, post_file in enumerate(posts, 1):
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            title = data.get('title', '无标题')
            # 缩短长标题
            if len(title) > 30:
                title = title[:27] + "..."
            print(f"{i}. {title} ({post_file.name})")
        except:
            print(f"{i}. {post_file.name} (读取失败)")

    choice = input(f"\n选择要编辑的文章 (1-{len(posts)}, 输入0取消): ").strip()
    if choice == "0":
        return
    if not choice.isdigit() or not (1 <= int(choice) <= len(posts)):
        print("❌ 选择无效")
        return

    post_file = posts[int(choice) - 1]
    print(f"编辑: {post_file.name}")

    # 这里可以添加编辑逻辑，暂时只打开文件
    import platform
    system = platform.system()

    try:
        if system == "Windows":
            os.startfile(str(post_file))
        elif system == "Darwin":  # macOS
            subprocess.run(["open", str(post_file)])
        else:  # Linux
            subprocess.run(["xdg-open", str(post_file)])
        print(f"✅ 已用默认编辑器打开文件")
    except Exception as e:
        print(f"❌ 无法打开文件: {e}")
        print(f"📁 文件位置: {post_file.absolute()}")


def main():
    """主菜单"""
    print("\n" + "=" * 50)
    print("🎯 博客文章管理系统")
    print("=" * 50)
    print("1. ✨ 发布新文章")
    print("2. 📝 编辑现有文章")
    print("3. 📊 查看文章统计")
    print("4. 🚪 退出")
    print("=" * 50)

    choice = input("请选择 (1-4): ").strip()

    if choice == "1":
        create_post()
    elif choice == "2":
        edit_existing_post()
    elif choice == "3":
        show_stats()
    elif choice == "4":
        print("👋 再见！")
        sys.exit(0)
    else:
        print("❌ 选择无效")


def show_stats():
    """显示文章统计"""
    print("\n📊 文章统计")
    print("-" * 30)

    if not INDEX_FILE.exists():
        print("❌ 索引文件不存在")
        return

    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        print(f"文章总数: {len(index_data)}篇")

        # 标签统计
        tag_count = {}
        for post in index_data:
            for tag in post.get('tags', []):
                tag_count[tag] = tag_count.get(tag, 0) + 1

        if tag_count:
            print("\n🏷️ 标签统计:")
            for tag, count in sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {tag}: {count}篇")

        # 最新文章
        if index_data:
            latest = index_data[0]
            print(f"\n📅 最新文章: {latest.get('title', '无标题')}")
            print(f"   发布时间: {latest.get('date', '未知')}")
            print(f"   标签: {', '.join(latest.get('tags', []))}")

    except Exception as e:
        print(f"❌ 读取统计失败: {e}")


if __name__ == "__main__":
    try:
        while True:
            main()
            input("\n按回车键返回主菜单...")
    except KeyboardInterrupt:
        print("\n👋 程序退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        input("按回车键退出...")