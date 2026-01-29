// js/main.js
// 动态设置年份
document.getElementById('current-year') && (document.getElementById('current-year').textContent = new Date().getFullYear());

// 日志数据所在的文件夹路径
const POSTS_INDEX_URL = 'posts_index.json';
const POSTS_DIR = 'posts/';

// 主函数：在首页加载时列出所有日志
async function loadAllPosts() {
    const postsListEl = document.getElementById('posts-list');
    if (!postsListEl) return;

    try {
        // === 新增调试代码开始 ===
        console.log('🔍 [Main.js] 函数开始执行，正在获取文章列表...');
        // === 新增调试代码结束 ===

        const indexResp = await fetch(POSTS_INDEX_URL);
        if (!indexResp.ok) throw new Error('无法加载日志列表');
        const postsIndex = await indexResp.json();

        // === 新增调试代码：查看获取到的数据 ===
        console.log('✅ [Main.js] 成功获取到文章索引数据：', postsIndex);
        console.log('📊 [Main.js] 文章数量：', postsIndex.length);
        // === 新增调试代码结束 ===

        if (postsIndex.length === 0) {
            postsListEl.innerHTML = '<p class="no-posts">还没有日志，快去创建第一篇吧！</p>';
            return;
        }

        let postsHTML = '';
        // 按日期倒序排列，最新的在前
        postsIndex.sort((a, b) => new Date(b.id) - new Date(a.id));

        for (const postMeta of postsIndex) {
            postsHTML += `
                <div class="post-card" onclick="window.location.href='post.html?id=${postMeta.id}'">
                    <h3 class="post-title">${postMeta.title}</h3>
                    <span class="post-date"><i class="far fa-calendar"></i> ${postMeta.date} • <i class="far fa-clock"></i> ${postMeta.readTime}</span>
                    <p class="post-summary">${postMeta.summary}</p>
                    <a class="read-more">阅读全文 <i class="fas fa-arrow-right"></i></a>
                </div>
            `;
        }

        // === 新增调试代码：查看生成的HTML ===
        console.log('🛠️ [Main.js] 生成的HTML代码片段（前200字符）：', postsHTML.substring(0, 200));
        // === 新增调试代码结束 ===

        postsListEl.innerHTML = postsHTML;

    } catch (error) {
        console.error('❌ [Main.js] 加载日志列表失败:', error);
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