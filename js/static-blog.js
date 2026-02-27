// 简单的页面切换逻辑
function showHome() {
    // 隐藏所有页面
    document.querySelectorAll('.hidden').forEach(el => {
        el.style.display = 'none';
    });
    // 显示首页
    document.getElementById('homePage').style.display = 'block';
}

function toggleSidebar() {
    const header = document.querySelector('header');
    const toggleBtn = document.querySelector('.toggle-btn');
    
    if (header && toggleBtn) {
        header.classList.toggle('hidden');
        
        if (header.classList.contains('hidden')) {
            toggleBtn.textContent = '☰';
            document.body.classList.add('header-hidden');
        } else {
            toggleBtn.textContent = '◀';
            document.body.classList.remove('header-hidden');
        }
    }
}

// 处理页面加载和锚点导航
window.addEventListener('DOMContentLoaded', function() {
    // 检查URL中的锚点
    const hash = window.location.hash;
    if (hash) {
        // 隐藏首页
        const homePage = document.getElementById('homePage');
        if (homePage) {
            homePage.style.display = 'none';
        }
        
        // 显示对应页面
        const targetPage = document.querySelector(hash);
        if (targetPage) {
            targetPage.classList.remove('hidden');
            targetPage.style.display = 'block';
        } else {
            // 如果锚点不存在，显示首页
            const homePage = document.getElementById('homePage');
            if (homePage) {
                homePage.style.display = 'block';
            }
        }
    } else {
        // 如果没有锚点，确保首页显示
        const homePage = document.getElementById('homePage');
        if (homePage) {
            homePage.style.display = 'block';
        }
        
        // 隐藏所有hidden类的元素
        document.querySelectorAll('.hidden').forEach(el => {
            el.style.display = 'none';
        });
    }

    // 为导航链接添加点击事件
    document.querySelectorAll('nav a, .footer-links a').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                
                // 隐藏首页
                const homePage = document.getElementById('homePage');
                if (homePage) {
                    homePage.style.display = 'none';
                }
                
                // 显示对应页面
                if (href === '#') {
                    // 对于首页链接，显示首页
                    const homePage = document.getElementById('homePage');
                    if (homePage) {
                        homePage.style.display = 'block';
                    }
                    
                    // 隐藏所有hidden类的元素
                    document.querySelectorAll('.hidden').forEach(el => {
                        el.classList.add('hidden');
                        el.style.display = 'none';
                    });
                } else {
                    // 先移除目标页面的hidden类，避免被隐藏
                    const targetPage = document.querySelector(href);
                    if (targetPage) {
                        targetPage.classList.remove('hidden');
                    }
                    
                    // 隐藏所有hidden类的元素
                    document.querySelectorAll('.hidden').forEach(el => {
                        el.style.display = 'none';
                    });
                    
                    // 显示目标页面
                    if (targetPage) {
                        targetPage.style.display = 'block';
                    }
                }
                
                // 更新URL锚点
                window.location.hash = href;
            }
        });
    });

    // 为文章链接添加点击事件
    document.querySelectorAll('.post-card-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // 只对锚点链接执行阻止默认行为和页面切换逻辑
            if (href.startsWith('#')) {
                e.preventDefault();
                
                // 隐藏所有页面
                document.querySelectorAll('#homePage, .hidden').forEach(el => {
                    el.style.display = 'none';
                });
                
                // 显示对应文章
                const targetPost = document.querySelector(href);
                if (targetPost) {
                    targetPost.style.display = 'block';
                } else {
                    document.getElementById('homePage').style.display = 'block';
                }
                
                // 更新URL锚点
                window.location.hash = href;
            }
        });
    });

    // 搜索功能
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    
    if (searchInput && searchBtn) {
        // 创建消息提示元素
        function createMessageElement() {
            let messageEl = document.getElementById('search-message');
            if (!messageEl) {
                messageEl = document.createElement('div');
                messageEl.id = 'search-message';
                messageEl.className = 'search-message';
                searchInput.parentElement.parentElement.appendChild(messageEl);
            }
            return messageEl;
        }
        
        // 显示消息
        function showMessage(text, type = 'info') {
            const messageEl = createMessageElement();
            messageEl.textContent = text;
            messageEl.className = `search-message search-message-${type}`;
            messageEl.style.display = 'block';
            
            // 3秒后自动隐藏
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 3000);
        }
        
        function performSearch() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            
            if (!searchTerm) {
                showMessage('请输入搜索关键词', 'error');
                return;
            }
            
            // 添加搜索中反馈
            const originalBtnText = searchBtn.textContent;
            searchBtn.textContent = '搜索中...';
            searchBtn.disabled = true;
            
            // 短暂延迟模拟搜索过程
            setTimeout(() => {
                const postCards = document.querySelectorAll('.post-card-link');
                let foundCount = 0;
                
                postCards.forEach(card => {
                    const title = card.querySelector('.post-title').textContent.toLowerCase();
                    const excerpt = card.querySelector('.post-excerpt').textContent.toLowerCase();
                    const tags = card.querySelector('.post-tags').textContent.toLowerCase();
                    
                    if (title.includes(searchTerm) || excerpt.includes(searchTerm) || tags.includes(searchTerm)) {
                        card.style.display = 'block';
                        foundCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });
                
                // 恢复按钮状态
                searchBtn.textContent = originalBtnText;
                searchBtn.disabled = false;
                
                // 显示搜索结果反馈
                if (foundCount > 0) {
                    showMessage(`找到 ${foundCount} 篇相关文章`);
                } else {
                    showMessage('没有找到相关文章，请尝试其他关键词', 'error');
                }
            }, 500);
        }
        
        searchBtn.addEventListener('click', performSearch);
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
});
