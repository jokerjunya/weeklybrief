// Weekly Report Interactive Features
class WeeklyReportApp {
    constructor() {
        this.isDarkMode = false;
        this.currentFilter = 'all';
        this.newsData = [];
        
        this.init();
    }

    async init() {
        this.setupTheme();
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        await this.loadNewsData();
        this.setupNewsFilters();
        this.setupIntersectionObserver();
        this.setupProgressBars();
        this.setupExportFeature();
    }

    setupEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    async loadNewsData() {
        // 実際のMDファイルからニュースデータを読み込む
        try {
            // JSONファイルから最新のニュースデータを読み込み
            const response = await fetch('news-data.json');
            if (response.ok) {
                const data = await response.json();
                this.newsData = data.articles || [];
                
                // サマリーも更新
                const summaryElement = document.querySelector('.news-summary p');
                if (summaryElement && data.summary) {
                    summaryElement.textContent = data.summary;
                }
                
                console.log(`✅ ニュースデータ読み込み完了: ${this.newsData.length}件`);
                console.log(`📅 生成日時: ${data.generated_at}`);
                return;
            }
            
            // フォールバック: JSONファイルが読み込めない場合
            console.warn('⚠️ news-data.jsonが読み込めません。フォールバックデータを使用します。');
            this.newsData = [
                {
                    category: 'openai',
                    title: 'Payment infrastructure startup Polar raises $10 million',
                    summary: 'AI関連スタートアップ、大型資金調達',
                    url: 'https://www.finextra.com/newsarticle/46179/payment-infrastructure-startup-polar-raises-10-million',
                    time: '06/19 08:56',
                    source: 'OpenAI'
                },
                {
                    category: 'openai',
                    title: 'composio-openai-agents 1.0.0rc4',
                    summary: 'AI業界: composio-openai-agents 1...',
                    url: 'https://pypi.org/project/composio-openai-agents/1.0.0rc4/',
                    time: '06/19 08:07',
                    source: 'OpenAI'
                },
                {
                    category: 'openai',
                    title: 'composio-openai 1.0.0rc4',
                    summary: 'AI業界: composio-openai 1...',
                    url: 'https://pypi.org/project/composio-openai/1.0.0rc4/',
                    time: '06/19 08:07',
                    source: 'OpenAI'
                },
                {
                    category: 'gemini',
                    title: 'How to reduce the environmental impact of using AI',
                    summary: 'AI業界: How to reduce the environmenta...',
                    url: 'https://onlinejournalismblog.com/2025/06/19/how-to-reduce-the-environmental-impact-of-using-ai/',
                    time: '06/19 08:44',
                    source: 'Gemini'
                },
                {
                    category: 'gemini',
                    title: 'Google\'s AI Mode Now Supports Voice Chats With New \'Search Live Feature',
                    summary: 'Google、AI新機能を発表',
                    url: 'https://www.thurrott.com/a-i/322314/googles-ai-mode-now-supports-voice-chats-with-new-search-live-feature',
                    time: '06/19 08:33',
                    source: 'Gemini'
                },
                {
                    category: 'gemini',
                    title: 'gemini-model 0.2.4',
                    summary: 'AI業界: gemini-model 0...',
                    url: 'https://pypi.org/project/gemini-model/0.2.4/',
                    time: '06/19 08:32',
                    source: 'Gemini'
                },
                {
                    category: 'other',
                    title: '"Embarrassment" Of Pandas Might Be The Funniest Collective Noun In The Wild',
                    summary: 'AI業界: "Embarrassment" Of Pandas Migh...',
                    url: 'https://www.boredpanda.com/what-is-a-group-of-pandas-called/',
                    time: '06/19 07:41',
                    source: 'Lovable'
                },
                {
                    category: 'other',
                    title: 'The Waterfront Review: Topher Grace Single-Handedly Saves Netflix\'s Ozark Replacement After A Slow & Choppy Start',
                    summary: 'AI業界: The Waterfront Review: Topher...',
                    url: 'https://screenrant.com/the-waterfront-tv-review/',
                    time: '06/19 07:01',
                    source: 'Lovable'
                },
                {
                    category: 'other',
                    title: 'Holt McCallany on Mindhunter, David Fincher, and masculinity: \'My mother would\'ve berated me for trying to split the bill with a woman\'',
                    summary: 'AI業界: Holt McCallany on Mindhunter,...',
                    url: 'https://www.the-independent.com/arts-entertainment/tv/features/holt-mccallany-mindhunter-waterfront-netflix-b2772498.html',
                    time: '06/19 05:07',
                    source: 'Lovable'
                },
                {
                    category: 'other',
                    title: 'Cannes Briefing: What the ad industry isn\'t saying about AI',
                    summary: 'AI業界: Cannes Briefing: What the ad i...',
                    url: 'http://digiday.com/marketing/cannes-briefing-what-the-ad-industry-isnt-saying-about-ai/',
                    time: '06/19 04:01',
                    source: 'Perplexity'
                },
                {
                    category: 'other',
                    title: 'Middle-aged man dressing as a little girl given license to drive a school bus—hangs a sign in window that reads \'Lolita Line\'',
                    summary: 'AI業界: Middle-aged man dressing as a...',
                    url: 'https://www.americanthinker.com/blog/2025/06/middle_aged_man_dressing_as_a_little_girl_given_license_to_drive_a_school_bus_hangs_a_sign_in_window_that_reads_lolita_line.html',
                    time: '06/19 04:00',
                    source: 'Grok'
                }
            ];

            console.log(`✅ フォールバックデータ読み込み完了: ${this.newsData.length}件`);
            
        } catch (error) {
            console.error('Error loading news data:', error);
            this.newsData = [];
        }
    }

    // Theme Management
    setupTheme() {
        const savedTheme = localStorage.getItem('weekly-report-theme') || 'light';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        this.isDarkMode = theme === 'dark';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('weekly-report-theme', theme);
        
        const themeButton = document.querySelector('.theme-toggle');
        const icon = themeButton.querySelector('i');
        const text = themeButton.querySelector('span');
        
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
            text.textContent = 'ライトモード';
        } else {
            icon.className = 'fas fa-moon';
            text.textContent = 'ダークモード';
        }
    }

    toggleTheme() {
        const newTheme = this.isDarkMode ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    // News Filtering
    setupNewsFilters() {
        this.renderNews(); // ニュースを描画
        
        const filterButtons = document.querySelectorAll('.category-btn');

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const category = button.dataset.category;
                this.filterNews(category, filterButtons);
            });
        });
    }

    renderNews() {
        const newsGrid = document.getElementById('newsGrid');
        if (!newsGrid || !this.newsData.length) return;

        newsGrid.innerHTML = this.newsData.map(article => `
            <div class="news-card" data-category="${article.category}">
                <div class="news-header">
                    <span class="news-category ${article.category}">${article.source}</span>
                    <span class="news-time">${article.time}</span>
                </div>
                <h3 class="news-title">${article.title}</h3>
                <p class="news-excerpt">${article.summary}</p>
                <div class="news-footer">
                    <a href="${article.url}" class="news-link" target="_blank" rel="noopener noreferrer">
                        <span>記事を読む</span>
                        <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            </div>
        `).join('');
    }

    filterNews(category, buttons) {
        this.currentFilter = category;
        const cards = document.querySelectorAll('.news-card');
        
        // Update button states
        buttons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.category === category);
        });

        // Filter cards with animation
        cards.forEach(card => {
            const cardCategory = card.dataset.category;
            const shouldShow = category === 'all' || cardCategory === category;
            
            if (shouldShow) {
                card.style.display = 'block';
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.opacity = '1';
                }, 50);
            } else {
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.display = 'none';
                }, 200);
            }
        });
    }

    // Keyboard Shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ignore if user is typing in an input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            switch(e.key.toLowerCase()) {
                case 't':
                    e.preventDefault();
                    this.toggleTheme();
                    break;
                case 'e':
                    e.preventDefault();
                    this.exportReport();
                    break;
                case '1':
                    e.preventDefault();
                    this.filterNewsByKey('all');
                    break;
                case '2':
                    e.preventDefault();
                    this.filterNewsByKey('openai');
                    break;
                case '3':
                    e.preventDefault();
                    this.filterNewsByKey('gemini');
                    break;
                case '4':
                    e.preventDefault();
                    this.filterNewsByKey('other');
                    break;
            }
        });
    }

    filterNewsByKey(category) {
        const buttons = document.querySelectorAll('.category-btn');
        this.filterNews(category, buttons);
    }

    // Intersection Observer for Animations
    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe all animated elements
        const animatedElements = document.querySelectorAll('.metric-card, .stock-card, .news-card, .schedule-item');
        animatedElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(10px)';
            el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            observer.observe(el);
        });
    }

    // Progress Bar Animations
    setupProgressBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        
        const animateProgressBar = (bar) => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 500);
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateProgressBar(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });

        progressBars.forEach(bar => observer.observe(bar));
    }

    // Export Feature
    setupExportFeature() {
        // Export functionality will be implemented here
    }

    exportReport() {
        // Create a simplified version for export
        const reportData = {
            date: new Date().toLocaleDateString('ja-JP'),
            metrics: this.extractMetricsData(),
            stocks: this.extractStockData(),
            news: this.extractNewsData(),
            schedule: this.extractScheduleData()
        };

        // Convert to JSON and download
        const dataStr = JSON.stringify(reportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `weekly-report-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        
        // Show success message
        this.showNotification('レポートをエクスポートしました', 'success');
    }

    extractMetricsData() {
        const metrics = [];
        const metricCards = document.querySelectorAll('.metric-card');
        
        metricCards.forEach(card => {
            const title = card.querySelector('.metric-title h3').textContent;
            const value = card.querySelector('.value-number').textContent;
            const unit = card.querySelector('.value-unit').textContent;
            const changes = Array.from(card.querySelectorAll('.change-item')).map(item => 
                item.textContent.trim()
            );
            
            metrics.push({ title, value, unit, changes });
        });
        
        return metrics;
    }

    extractStockData() {
        const stocks = [];
        const stockCards = document.querySelectorAll('.stock-card');
        
        stockCards.forEach(card => {
            const name = card.querySelector('.stock-header h3').textContent;
            const symbol = card.querySelector('.stock-symbol').textContent;
            const price = card.querySelector('.price-value').textContent;
            const change = card.querySelector('.price-change span').textContent;
            
            stocks.push({ name, symbol, price, change });
        });
        
        return stocks;
    }

    extractNewsData() {
        const news = [];
        const newsCards = document.querySelectorAll('.news-card');
        
        newsCards.forEach(card => {
            const category = card.querySelector('.news-category').textContent;
            const title = card.querySelector('.news-title').textContent;
            const excerpt = card.querySelector('.news-excerpt').textContent;
            const time = card.querySelector('.news-time').textContent;
            
            news.push({ category, title, excerpt, time });
        });
        
        return news;
    }

    extractScheduleData() {
        const schedule = [];
        const scheduleItems = document.querySelectorAll('.schedule-item');
        
        scheduleItems.forEach(item => {
            const day = item.querySelector('.date-day').textContent;
            const month = item.querySelector('.date-month').textContent;
            const title = item.querySelector('.schedule-content h3').textContent;
            const time = item.querySelector('.schedule-time span').textContent;
            
            schedule.push({ day, month, title, time });
        });
        
        return schedule;
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            transition: all 0.3s ease;
            transform: translateX(100%);
        `;
        
        if (type === 'success') {
            notification.style.backgroundColor = '#10b981';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#ef4444';
        } else {
            notification.style.backgroundColor = '#3b82f6';
        }
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Global functions for HTML onclick handlers
function toggleTheme() {
    window.reportApp.toggleTheme();
}

function exportReport() {
    window.reportApp.exportReport();
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.reportApp = new WeeklyReportApp();
});

// Handle window resize for responsive adjustments
window.addEventListener('resize', () => {
    // Adjust layout if needed for responsive design
    const container = document.querySelector('.container');
    if (window.innerWidth < 768) {
        container.classList.add('mobile-layout');
    } else {
        container.classList.remove('mobile-layout');
    }
});

// Performance optimization: Debounce scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Smooth scrolling for anchor links
document.addEventListener('click', (e) => {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Add loading states for dynamic content
function showLoading(element) {
    element.style.opacity = '0.6';
    element.style.pointerEvents = 'none';
}

function hideLoading(element) {
    element.style.opacity = '1';
    element.style.pointerEvents = 'auto';
}

// Console welcome message
console.log('%c📊 週次レポート Dashboard', 'color: #3b82f6; font-size: 16px; font-weight: bold;');
console.log('%cキーボードショートカット:', 'color: #6b7280; font-size: 14px;');
console.log('%c  T: テーマ切り替え', 'color: #6b7280; font-size: 12px;');
console.log('%c  E: エクスポート', 'color: #6b7280; font-size: 12px;');
console.log('%c  1-4: ニュースフィルター', 'color: #6b7280; font-size: 12px;'); 