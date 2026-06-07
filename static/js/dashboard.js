/**
 * RAFEEQ Dashboard JavaScript
 * Handles sidebar interactions, animations, and dynamic content
 */

document.addEventListener('DOMContentLoaded', function () {
    // ==================== SIDEBAR FUNCTIONALITY ====================

    const sidebar = document.getElementById('rafeeqSidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const navLinks = document.querySelectorAll('.nav-link');

    // Toggle sidebar on mobile
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
            sidebarOverlay.classList.toggle('show');

            // Animate toggle button
            this.style.transform = sidebar.classList.contains('show') ? 'rotate(90deg)' : 'rotate(0deg)';
        });
    }

    // Close sidebar when clicking overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function () {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
            if (sidebarToggle) {
                sidebarToggle.style.transform = 'rotate(0deg)';
            }
        });
    }

    // Close sidebar when clicking a link on mobile
    navLinks.forEach(link => {
        link.addEventListener('click', function () {
            if (window.innerWidth <= 992) {
                sidebar.classList.remove('show');
                sidebarOverlay.classList.remove('show');
                if (sidebarToggle) {
                    sidebarToggle.style.transform = 'rotate(0deg)';
                }
            }
        });
    });

    // ==================== CARD ANIMATIONS ====================

    const statCards = document.querySelectorAll('.stat-card-new');
    const actionCards = document.querySelectorAll('.action-card');
    const sectionCards = document.querySelectorAll('.section-card-large');

    // Add hover effects to stat cards
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.zIndex = '10';
        });

        card.addEventListener('mouseleave', function () {
            this.style.zIndex = '1';
        });
    });

    // Add click effect to action cards
    actionCards.forEach(card => {
        card.addEventListener('click', function (e) {
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });

    // Add hover effects to section cards
    sectionCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.zIndex = '10';
        });

        card.addEventListener('mouseleave', function () {
            this.style.zIndex = '1';
        });
    });

    // ==================== SEARCH FUNCTIONALITY ====================

    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');
    const tableRows = document.querySelectorAll('.table-new tbody tr');

    if (searchInput && searchBtn) {
        // Search on button click
        searchBtn.addEventListener('click', function () {
            performSearch();
        });

        // Search on Enter key
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });

        // Real-time search
        searchInput.addEventListener('input', function () {
            performSearch();
        });
    }

    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase();

        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
                row.style.animation = 'fadeIn 0.3s ease';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // ==================== STATISTICS COUNTER ANIMATION ====================

    const statValues = document.querySelectorAll('.stat-value');

    function animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = end > start ? 1 : -1;
        const stepTime = Math.abs(Math.floor(duration / range));
        let current = start;

        const timer = setInterval(function () {
            current += increment;
            element.textContent = current;
            if (current === end) {
                clearInterval(timer);
            }
        }, stepTime);
    }

    // Animate counters on page load
    statValues.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        if (!isNaN(finalValue)) {
            stat.textContent = '0';
            setTimeout(() => {
                animateValue(stat, 0, finalValue, 1000);
            }, 300);
        }
    });

    // ==================== RESPONSIVE HANDLING ====================

    function handleResize() {
        if (window.innerWidth > 992) {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
            if (sidebarToggle) {
                sidebarToggle.style.transform = 'rotate(0deg)';
            }
        }
    }

    window.addEventListener('resize', handleResize);

    // ==================== SMOOTH SCROLL ====================

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ==================== TOOLTIPS ====================

    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // ==================== NOTIFICATION BADGE ANIMATION ====================

    const notificationBadges = document.querySelectorAll('.notification-badge');

    notificationBadges.forEach(badge => {
        if (parseInt(badge.textContent) > 0) {
            badge.style.animation = 'pulse 2s infinite';
        }
    });

    // ==================== LOADING STATES ====================

    const buttons = document.querySelectorAll('.btn-enter-section');

    buttons.forEach(button => {
        button.addEventListener('click', function (e) {
            if (!this.classList.contains('loading')) {
                this.classList.add('loading');
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';

                // Remove loading state after navigation (or timeout)
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.innerHTML = originalText;
                }, 2000);
            }
        });
    });

    // ==================== KEYBOARD SHORTCUTS ====================

    document.addEventListener('keydown', function (e) {
        // Ctrl/Cmd + K: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape: Close sidebar on mobile
        if (e.key === 'Escape') {
            if (sidebar && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
                sidebarOverlay.classList.remove('show');
                if (sidebarToggle) {
                    sidebarToggle.style.transform = 'rotate(0deg)';
                }
            }
        }
    });

    // ==================== FADE-IN ANIMATION ON SCROLL ====================

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.stat-card-new, .action-card, .section-card-large').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // ==================== CONSOLE WELCOME MESSAGE ====================

    console.log('%cRAFEEQ Dashboard', 'color: #1a237e; font-size: 24px; font-weight: bold;');
    console.log('%cWelcome to the Inclusive Employment Platform', 'color: #6a1b9a; font-size: 14px;');
    console.log('%cVersion 1.0.0', 'color: #666; font-size: 12px;');
});

// ==================== UTILITY FUNCTIONS ====================

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

/**
 * Confirm action
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// ==================== CSS ANIMATIONS ====================

const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
`;
document.head.appendChild(style);
