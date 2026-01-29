class ReadingProgress {
    constructor() {
        this.progressBar = document.getElementById('reading-progress');
        if (!this.progressBar) return;
        
        this.article = document.querySelector('article');
        if (!this.article) return;
        
        this.init();
    }
    
    init() {
        window.addEventListener('scroll', this.updateProgress.bind(this));
        window.addEventListener('resize', this.updateProgress.bind(this));
        this.updateProgress();
    }
    
    updateProgress() {
        const articleRect = this.article.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        // 计算文章在视口中的可见比例
        const articleTop = this.article.offsetTop;
        const articleHeight = this.article.offsetHeight;
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop >= articleTop) {
            const scrolled = scrollTop - articleTop;
            const progress = Math.min((scrolled / (articleHeight - windowHeight)) * 100, 100);
            this.progressBar.style.width = `${progress}%`;
            this.progressBar.style.opacity = progress > 0 ? '1' : '0';
        } else {
            this.progressBar.style.opacity = '0';
        }
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    new ReadingProgress();
});