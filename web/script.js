// Theme Management
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.setTheme(this.theme);
        this.bindEvents();
    }

    setTheme(theme) {
        this.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.updateThemeButton();
    }

    toggleTheme() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    updateThemeButton() {
        const button = document.getElementById('themeToggle');
        const icon = button.querySelector('i');
        
        if (this.theme === 'dark') {
            icon.className = 'fas fa-sun';
            button.setAttribute('aria-label', 'ライトモードに切り替え');
        } else {
            icon.className = 'fas fa-moon';
            button.setAttribute('aria-label', 'ダークモードに切り替え');
        }
    }

    bindEvents() {
        const themeToggle = document.getElementById('themeToggle');
        themeToggle.addEventListener('click', () => this.toggleTheme());
    }
}

// News Filter Manager
class NewsFilterManager {
    constructor() {
        this.activeCategory = 'all';
        this.init();
    }

    init() {
        this.bindEvents();
        this.filterNews(this.activeCategory);
    }

    bindEvents() {
        const categoryButtons = document.querySelectorAll('.category-btn');
        categoryButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const category = e.target.getAttribute('data-category');
                this.setActiveCategory(category);
                this.filterNews(category);
            });
        });
    }

    setActiveCategory(category) {
        // Remove active class from all buttons
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Add active class to clicked button
        document.querySelector(`[data-category="${category}"]`).classList.add('active');
        this.activeCategory = category;
    }

    filterNews(category) {
        const newsCards = document.querySelectorAll('.news-card');
        
        newsCards.forEach(card => {
            const cardCategory = card.getAttribute('data-category');
            
            if (category === 'all' || cardCategory === category) {
                card.style.display = 'block';
                card.style.animation = 'fadeInUp 0.4s ease-out';
            } else {
                card.style.display = 'none';
            }
        });

        this.updateNewsCount();
    }

    updateNewsCount() {
        const visibleCards = document.querySelectorAll('.news-card[style*="block"]').length;
        const totalCards = document.querySelectorAll('.news-card').length;
        
        // Update section subtitle with count
        const subtitle = document.querySelector('.section:last-of-type .section-subtitle');
        if (this.activeCategory === 'all') {
            subtitle.textContent = `AI業界の最新動向（${totalCards}件）`;
        } else {
            subtitle.textContent = `AI業界の最新動向（${visibleCards}件表示）`;
        }
    }
}

// Progress Bar Animation
class ProgressBarAnimator {
    constructor() {
        this.init();
    }

    init() {
        this.animateProgressBars();
    }

    animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        
        // Use Intersection Observer for scroll-triggered animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const width = progressBar.style.width;
                    
                    // Reset width and animate
                    progressBar.style.width = '0%';
                    setTimeout(() => {
                        progressBar.style.width = width;
                    }, 100);
                }
            });
        }, {
            threshold: 0.5
        });

        progressBars.forEach(bar => observer.observe(bar));
    }
}

// Metric Card Hover Effects
class MetricCardEnhancer {
    constructor() {
        this.init();
    }

    init() {
        this.addHoverEffects();
        this.addClickEffects();
    }

    addHoverEffects() {
        const metricCards = document.querySelectorAll('.metric-card');
        
        metricCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px) scale(1.02)';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    addClickEffects() {
        const metricCards = document.querySelectorAll('.metric-card');
        
        metricCards.forEach(card => {
            card.addEventListener('click', () => {
                // Add pulse effect
                card.style.animation = 'pulse 0.3s ease-in-out';
                setTimeout(() => {
                    card.style.animation = '';
                }, 300);
            });
        });
    }
}

// Export Functionality
class ExportManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        const exportBtn = document.querySelector('.export-btn');
        exportBtn.addEventListener('click', () => this.exportReport());
    }

    exportReport() {
        // Show loading state
        const exportBtn = document.querySelector('.export-btn');
        const originalText = exportBtn.innerHTML;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> エクスポート中...';
        exportBtn.disabled = true;

        // Simulate export process
        setTimeout(() => {
            this.generatePDF();
            
            // Reset button
            exportBtn.innerHTML = originalText;
            exportBtn.disabled = false;
        }, 2000);
    }

    generatePDF() {
        // In a real implementation, you would use a library like jsPDF or Puppeteer
        // For now, we'll create a simple text export
        const reportData = this.collectReportData();
        const blob = new Blob([reportData], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `週次レポート_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        // Show success message
        this.showNotification('レポートがエクスポートされました', 'success');
    }

    collectReportData() {
        const title = document.querySelector('.header-title h1').textContent;
        const date = document.querySelector('.header-date').textContent;
        
        let reportText = `${title} - ${date}\n\n`;
        
        // Business metrics
        reportText += "=== ビジネス実績 ===\n";
        const metricCards = document.querySelectorAll('.metric-card');
        metricCards.forEach(card => {
            const serviceName = card.querySelector('.metric-title h3').textContent;
            const metricType = card.querySelector('.metric-type').textContent;
            const value = card.querySelector('.value-number').textContent + card.querySelector('.value-unit').textContent;
            const changes = Array.from(card.querySelectorAll('.change-item')).map(item => item.textContent).join(', ');
            
            reportText += `${serviceName} (${metricType}): ${value} - ${changes}\n`;
        });

        // Stock data
        reportText += "\n=== 株価情報 ===\n";
        const stockCards = document.querySelectorAll('.stock-card');
        stockCards.forEach(card => {
            const stockName = card.querySelector('.stock-header h3').textContent;
            const symbol = card.querySelector('.stock-symbol').textContent;
            const price = card.querySelector('.price-value').textContent;
            const change = card.querySelector('.price-change').textContent;
            
            reportText += `${stockName} (${symbol}): ${price} ${change}\n`;
        });

        // Schedule
        reportText += "\n=== 今週のスケジュール ===\n";
        const scheduleItems = document.querySelectorAll('.schedule-item');
        scheduleItems.forEach(item => {
            const date = item.querySelector('.date-day').textContent + ' ' + item.querySelector('.date-month').textContent;
            const title = item.querySelector('.schedule-content h3').textContent;
            const time = item.querySelector('.schedule-time').textContent;
            
            reportText += `${date}: ${title} ${time}\n`;
        });

        return reportText;
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--success);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Keyboard Navigation
class KeyboardNavigationManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindKeyboardEvents();
    }

    bindKeyboardEvents() {
        document.addEventListener('keydown', (e) => {
            // Theme toggle with 'T' key
            if (e.key === 't' || e.key === 'T') {
                if (!e.target.matches('input, textarea')) {
                    e.preventDefault();
                    document.getElementById('themeToggle').click();
                }
            }

            // Export with 'E' key
            if (e.key === 'e' || e.key === 'E') {
                if (!e.target.matches('input, textarea')) {
                    e.preventDefault();
                    document.querySelector('.export-btn').click();
                }
            }

            // News filter with number keys
            if (e.key >= '1' && e.key <= '4') {
                if (!e.target.matches('input, textarea')) {
                    e.preventDefault();
                    const categories = ['all', 'openai', 'gemini', 'other'];
                    const categoryIndex = parseInt(e.key) - 1;
                    if (categories[categoryIndex]) {
                        document.querySelector(`[data-category="${categories[categoryIndex]}"]`).click();
                    }
                }
            }
        });
    }
}

// Add custom CSS animations
const additionalStyles = `
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

.metric-card {
    cursor: pointer;
}

.metric-card:active {
    transform: translateY(-2px) scale(0.98);
}
`;

// Initialize all managers when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add additional styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = additionalStyles;
    document.head.appendChild(styleSheet);

    // Initialize all functionality
    new ThemeManager();
    new NewsFilterManager();
    new ProgressBarAnimator();
    new MetricCardEnhancer();
    new ExportManager();
    new KeyboardNavigationManager();

    // Add keyboard shortcuts help
    const helpText = document.createElement('div');
    helpText.innerHTML = `
        <div style="position: fixed; bottom: 20px; left: 20px; font-size: 0.75rem; color: var(--text-tertiary); opacity: 0.7;">
            キーボードショートカット: T (テーマ切り替え) | E (エクスポート) | 1-4 (ニュースフィルター)
        </div>
    `;
    document.body.appendChild(helpText);

    console.log('📊 週次レポートWebページが初期化されました');
    console.log('🎯 キーボードショートカット: T=テーマ切り替え, E=エクスポート, 1-4=ニュースフィルター');
}); 