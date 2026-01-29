// js/main.js
// 动态设置年份
document.getElementById('current-year') && (document.getElementById('current-year').textContent = new Date().getFullYear());

// 日志数据所在的文件夹路径
const POSTS_DIR = 'posts/';

// 主函数：在首页加载时列出所有日志
async function loadAllPosts() {
    const postsListEl = document.getElementById('posts-list');
    if (!postsListEl) return; // 如果不是首页，则退出

    try {
        // 注意：在实际部署时，你需要一个文件列表接口。
        // 此处为演示，我们假设已知日志文件名，或通过其他方式获取列表。
        // 示例：手动维护一个日志列表数组。
        const postFiles = [
            '2024-05-20-hello-world.json',
            // 你可以在这里添加更多的日志文件名
        ];

        if (postFiles.length === 0) {
            postsListEl.innerHTML = '<p class="no-posts">还没有日志，快去创建第一篇吧！</p>';
            return;
        }

        let postsHTML = '';
        for (const filename of postFiles) {
            const resp = await fetch(POSTS_DIR + filename);
            if (!resp.ok) continue;
            const post = await resp.json();

            postsHTML += `
                <div class="post-card" onclick="window.location.href='post.html?id=${filename.replace('.json', '')}'">
                    <h3 class="post-title">${post.title}</h3>
                    <span class="post-date"><i class="far fa-calendar"></i> ${post.date} • <i class="far fa-clock"></i> ${post.readTime}</span>
                    <p class="post-summary">${post.summary}</p>
                    <a class="read-more">阅读全文 <i class="fas fa-arrow-right"></i></a>
                </div>
            `;
        }
        postsListEl.innerHTML = postsHTML;

    } catch (error) {
        console.error('加载日志列表失败:', error);
        postsListEl.innerHTML = '<p class="error">加载日志时出错，请稍后重试。</p>';
    }
}

// 函数：在post.html页面加载单篇日志
async function loadSinglePost(postId) {
    const postContentEl = document.getElementById('post-content');
    if (!postContentEl) return;

    try {
        const resp = await fetch(`${POSTS_DIR}${postId}.json`);
        if (!resp.ok) throw new Error('日志未找到');
        const post = await resp.json();

        // 构建完整的日志HTML
        // 注意：为了安全，如果日志内容来自用户，应进行适当的转义
        const bodyHTML = post.body.replace(/\n/g, '<br>'); // 简单将换行转为<br>

        postContentEl.innerHTML = `
            <h1>${post.title}</h1>
            <div class="post-meta">
                <span><i class="far fa-calendar"></i> ${post.date}</span> • 
                <span><i class="far fa-clock"></i> ${post.readTime}</span> •
                <span><i class="far fa-heart"></i> ${post.mood}</span>
            </div>
            <div class="post-body">
                ${bodyHTML}
            </div>
            <p style="margin-top: 2rem;">
                <a href="index.html" class="back-link"><i class="fas fa-arrow-left"></i> 返回首页</a>
            </p>
        `;

        // 更新页面标题
        document.title = `${post.title} - 我的日常手记`;

    } catch (error) {
        console.error('加载单篇日志失败:', error);
        postContentEl.innerHTML = '<p class="error">日志加载失败或不存在。</p>';
    }
}

// 主题切换功能
async function initThemeSwitcher() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    // 检查本地存储或系统偏好
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    const currentTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    themeToggle.innerHTML = currentTheme === 'dark' 
        ? '<i class="fas fa-sun"></i>' 
        : '<i class="fas fa-moon"></i>';
    
    themeToggle.addEventListener('click', () => {
        const theme = document.documentElement.getAttribute('data-theme');
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        themeToggle.innerHTML = newTheme === 'dark' 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    });
}

// 在DOMContentLoaded中调用
document.addEventListener('DOMContentLoaded', initThemeSwitcher);

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 检查当前页面，执行对应的函数
    if (document.getElementById('posts-list')) {
        loadAllPosts(); // 首页：加载所有日志列表
    }
    // post.html 页面的单独逻辑已在它自己的script标签中
});