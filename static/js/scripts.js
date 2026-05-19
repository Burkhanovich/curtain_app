/* ===== MOBILE MENU ===== */
(function () {
    const btn = document.getElementById('mobileMenuBtn');
    const nav = document.getElementById('navMobile');
    if (!btn || !nav) return;

    btn.addEventListener('click', function () {
        const open = nav.style.display === 'block';
        nav.style.display = open ? 'none' : 'block';
        btn.textContent = open ? '☰' : '✕';
    });
})();

/* ===== CART BADGE (reads from Django session) ===== */
(function () {
    const badge = document.getElementById('cartCount');
    if (!badge) return;

    fetch('/cart/count/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(r => r.json())
        .then(data => {
            const count = data.count || 0;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        })
        .catch(() => { badge.style.display = 'none'; });
})();

/* ===== TOAST NOTIFICATIONS ===== */
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.borderLeftColor = type === 'error' ? '#EF4444'
                                : type === 'warning' ? '#EAB308'
                                : '#C9A84C';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 350);
    }, 3200);
}

/* ===== SMOOTH SCROLL ===== */
document.querySelectorAll('.scroll-link').forEach(function (link) {
    link.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        // Only handle same-page anchors
        if (!href || !href.includes('#')) return;
        const id = href.split('#')[1];
        const target = document.getElementById(id);
        if (!target) return;
        e.preventDefault();
        const headerH = document.querySelector('.header') ? document.querySelector('.header').offsetHeight : 0;
        window.scrollTo({ top: target.offsetTop - headerH - 16, behavior: 'smooth' });
    });
});

/* ===== PRODUCT GALLERY (detail page) ===== */
(function () {
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImg    = document.getElementById('mainImage');
    if (!thumbnails.length || !mainImg) return;

    thumbnails.forEach(function (thumb) {
        thumb.addEventListener('click', function () {
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            const src = this.dataset.image;
            if (src) {
                const img = mainImg.querySelector('img');
                if (img) img.src = src;
            }
        });
    });
})();

/* ===== OPTION BUTTONS (detail page) ===== */
document.querySelectorAll('.option-buttons').forEach(function (group) {
    group.querySelectorAll('.option-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            group.querySelectorAll('.option-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

/* ===== PRODUCT FILTER AUTO-SUBMIT ===== */
(function () {
    const filterForm = document.querySelector('.filters-section form');
    if (!filterForm) return;
    filterForm.querySelectorAll('select').forEach(function (sel) {
        sel.addEventListener('change', function () { filterForm.submit(); });
    });
})();

/* ===== CONTACT FORM ===== */
(function () {
    const form = document.getElementById('contactForm');
    if (!form) return;
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const success = document.getElementById('contactSuccess');
        if (success) {
            success.style.display = 'block';
            success.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        form.reset();
    });
})();

/* ===== CHECKOUT: delivery/payment option highlight ===== */
(function () {
    function initRadioHighlight(selector) {
        document.querySelectorAll(selector).forEach(function (label) {
            const radio = label.querySelector('input[type="radio"]');
            if (!radio) return;

            function update() {
                document.querySelectorAll(selector).forEach(function (l) {
                    l.style.borderColor = '';
                    l.style.background  = '';
                });
                if (radio.checked) {
                    label.style.borderColor = 'var(--gold)';
                    label.style.background  = 'var(--gold-pale)';
                }
            }
            radio.addEventListener('change', update);
            if (radio.checked) update();
        });
    }

    initRadioHighlight('.delivery-option');
    initRadioHighlight('.payment-option');
})();

/* ===== STAGGER ANIMATION for cards ===== */
(function () {
    const cards = document.querySelectorAll('.product-card, .category-card');
    cards.forEach(function (card, i) {
        card.style.animationDelay = (i * 0.06) + 's';
    });
})();
