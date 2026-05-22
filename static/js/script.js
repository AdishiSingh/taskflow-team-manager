/**
 * TaskFlow — UI interactions
 */

document.addEventListener('DOMContentLoaded', function () {
    initTheme();
    initToastsFromFlash();
    initTooltips();
    initConfirmations();
    initDateValidation();
    initFormValidation();
    initProgressAnimations();
    initLiveSearch();
    initStaggeredFadeIn();
});

/* ---------- Theme ---------- */
function initTheme() {
    const toggle = document.getElementById('themeToggle');
    const saved = localStorage.getItem('taskflow-theme') || 'light';
    applyTheme(saved);

    if (toggle) {
        toggle.addEventListener('click', function () {
            const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            applyTheme(next);
            localStorage.setItem('taskflow-theme', next);
            document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: next } }));
        });
    }
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.body.classList.toggle('theme-dark', theme === 'dark');
}

/* ---------- Toasts ---------- */
function initToastsFromFlash() {
    const el = document.getElementById('flash-messages');
    if (!el) return;
    try {
        const messages = JSON.parse(el.textContent);
        messages.forEach(([category, message], i) => {
            setTimeout(() => showToast(message, category), i * 120);
        });
    } catch (e) { /* ignore */ }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const icons = {
        success: 'bi-check-circle-fill',
        danger: 'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill'
    };

    const toast = document.createElement('div');
    toast.className = `toast-custom toast-custom-${type}`;
    toast.innerHTML = `
        <i class="bi ${icons[type] || icons.info} toast-icon"></i>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button type="button" class="toast-close" aria-label="Dismiss">&times;</button>
    `;

    container.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));

    const dismiss = () => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    };

    toast.querySelector('.toast-close').addEventListener('click', dismiss);
    setTimeout(dismiss, 4500);
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

/* ---------- Search ---------- */
function initLiveSearch() {
    document.querySelectorAll('[data-search-target]').forEach(input => {
        const target = document.querySelector(input.dataset.searchTarget);
        if (!target) return;
        const handler = debounce(() => filterSearchableRows(input.value, target), 200);
        input.addEventListener('input', handler);
    });

    const projectSearch = document.getElementById('projectProgressSearch');
    if (projectSearch) {
        projectSearch.addEventListener('input', debounce(function () {
            filterSearchableRows(projectSearch.value, document.getElementById('projectProgressTable'));
        }, 200));
    }

    const projectListSearch = document.getElementById('projectListSearch');
    if (projectListSearch) {
        projectListSearch.addEventListener('input', debounce(function () {
            const term = projectListSearch.value.toLowerCase();
            document.querySelectorAll('.project-search-item').forEach(card => {
                const text = card.dataset.search || '';
                card.style.display = text.includes(term) ? '' : 'none';
            });
        }, 200));
    }

    const taskSearch = document.getElementById('taskTableSearch');
    if (taskSearch) {
        taskSearch.addEventListener('input', debounce(function () {
            filterSearchableRows(taskSearch.value, document.getElementById('tasksTable'));
        }, 200));
    }
}

function filterSearchableRows(term, container) {
    if (!container) return;
    const q = term.toLowerCase().trim();
    container.querySelectorAll('.searchable-row').forEach(row => {
        const text = row.dataset.search || row.textContent.toLowerCase();
        row.style.display = !q || text.includes(q) ? '' : 'none';
    });
}

/* ---------- Animations ---------- */
function initStaggeredFadeIn() {
    document.querySelectorAll('.stat-row .stat-card, .activity-item, .chart-card').forEach((el, i) => {
        el.style.animationDelay = `${i * 0.05}s`;
        el.classList.add('stagger-in');
    });
}

function initProgressAnimations() {
    document.querySelectorAll('.progress-bar').forEach(bar => {
        let targetWidth = bar.getAttribute('aria-valuenow') || bar.dataset.width;
        if (!targetWidth) {
            const match = bar.style.width.match(/([\d.]+)%/);
            if (match) targetWidth = match[1];
        }
        const w = parseFloat(targetWidth);
        if (isNaN(w) || w < 0) return;
        bar.setAttribute('aria-valuenow', w);
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = w + '%'; }, 120);
    });
}

function initTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));
}

function initConfirmations() {
    document.querySelectorAll('form[onsubmit*="confirm"]').forEach(form => {
        form.addEventListener('submit', function (e) {
            const m = form.getAttribute('onsubmit').match(/confirm\('(.+?)'\)/);
            if (m && !confirm(m[1])) e.preventDefault();
        });
    });
}

function initDateValidation() {
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.addEventListener('change', function () {
            const selected = new Date(this.value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            this.classList.toggle('is-invalid', selected < today);
        });
    });
}

function initFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function (e) {
            let ok = true;
            form.querySelectorAll('[required]').forEach(f => {
                if (!f.value.trim()) { f.classList.add('is-invalid'); ok = false; }
                else f.classList.remove('is-invalid');
            });
            if (!ok) e.preventDefault();
        });
    });
}

function debounce(func, wait) {
    let t;
    return function (...args) {
        clearTimeout(t);
        t = setTimeout(() => func.apply(this, args), wait);
    };
}
