class BlogSearch {
    constructor() {
        this.postsIndex = [];
        this.searchInput = document.getElementById('search-input');
        this.searchResults = document.getElementById('search-results');
        
        if (this.searchInput) {
            this.init();
        }
    }
    
    async init() {
        try {
            await this.loadIndex();
            this.setupEventListeners();
            console.log('搜索功能初始化完成，加载了', this.postsIndex.length, '篇日志');
        } catch (error) {
            console.error('搜索功能初始化失败:', error);
        }
    }
    
    async loadIndex() {
        try {
            const response = await fetch('posts_index.json');
            if (!response.ok) throw new Error('无法加载日志索引');
            
            this.postsIndex = await response.json();
            console.log('成功加载日志索引:', this.postsIndex);
        } catch (error) {
            console.error('加载搜索索引失败:', error);
            // 如果失败，显示错误信息
            if (this.searchResults) {
                this.searchResults.innerHTML = `
                    <div class="no-results">
                        <p>搜索功能暂时不可用</p>
                    </div>
                `;
            }
        }
    }
    
    setupEventListeners() {
        // 输入框搜索
        let timeout;
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.performSearch(e.target.value.trim());
            }, 300);
        });
        
        // 点击外部关闭搜索结果
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && 
                !this.searchResults.contains(e.target)) {
                this.hideResults();
            }
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            // Ctrl+K 或 Cmd+K 聚焦搜索框
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.searchInput.focus();
            }
            
            // ESC 关闭搜索结果
            if (e.key === 'Escape') {
                this.hideResults();
                this.searchInput.blur();
            }
            
            // 上下箭头选择搜索结果
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                const items = this.searchResults.querySelectorAll('.search-result-item');
                if (items.length > 0) {
                    e.preventDefault();
                    this.handleArrowKeys(e.key, items);
                }
            }
        });
    }
    
    performSearch(query) {
        if (!query) {
            this.hideResults();
            return;
        }
        
        console.log('搜索关键词:', query);
        
        // 简单搜索算法：匹配标题、摘要、标签
        const results = this.postsIndex.filter(post => {
            const searchableText = `
                ${post.title || ''} 
                ${post.summary || ''} 
                ${post.tags ? post.tags.join(' ') : ''}
                ${post.keywords ? post.keywords.join(' ') : ''}
            `.toLowerCase();
            
            return searchableText.includes(query.toLowerCase());
        });
        
        console.log('找到结果:', results.length);
        this.displayResults(results, query);
    }
    
    displayResults(results, query) {
        if (!this.searchResults) return;
        
        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="no-results">
                    <p>没有找到包含"${query}"的日志</p>
                    <p class="search-snippet">试试其他关键词？</p>
                </div>
            `;
        } else {
            this.searchResults.innerHTML = results.map(post => `
                <a href="post.html?id=${post.id}" class="search-result-item">
                    <h4>${post.title}</h4>
                    <p class="search-snippet">${post.summary}</p>
                    <span class="search-meta">
                        <i class="far fa-calendar"></i> ${post.date} • 
                        <i class="far fa-clock"></i> ${post.readTime}
                        ${post.tags ? `• <i class="fas fa-tag"></i> ${post.tags.slice(0, 2).join(', ')}` : ''}
                    </span>
                </a>
            `).join('');
        }
        
        this.searchResults.style.display = 'block';
    }
    
    hideResults() {
        if (this.searchResults) {
            this.searchResults.style.display = 'none';
        }
    }
    
    handleArrowKeys(key, items) {
        const currentActive = document.activeElement;
        let currentIndex = -1;
        
        if (currentActive.classList.contains('search-result-item')) {
            currentIndex = Array.from(items).indexOf(currentActive);
        }
        
        let newIndex;
        if (key === 'ArrowDown') {
            newIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
        } else {
            newIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
        }
        
        items[newIndex].focus();
    }
}

// 页面加载后初始化搜索功能
document.addEventListener('DOMContentLoaded', () => {
    // 确保 posts_index.json 存在
    fetch('posts_index.json')
        .then(response => {
            if (response.ok) {
                new BlogSearch();
            } else {
                console.warn('posts_index.json 不存在或无法访问');
            }
        })
        .catch(error => {
            console.error('检查索引文件失败:', error);
        });
});