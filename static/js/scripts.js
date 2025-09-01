// ===== GLOBAL VARIABLES =====
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;

// Demo product data for frontend display
const products = {
    1: { id: 1, name: 'Oltin Klassik Parda', price: 350000, image: '🏺', category: 'classic' },
    2: { id: 2, name: 'Zamonaviy Oq Parda', price: 280000, image: '🎭', category: 'modern' },
    3: { id: 3, name: 'Hashamatli Bej Parda', price: 520000, image: '🌟', category: 'luxury' },
    4: { id: 4, name: 'Rangli Dizayn Parda', price: 420000, image: '🎨', category: 'modern' },
    5: { id: 5, name: 'Klassik Qizil Parda', price: 390000, image: '🏛️', category: 'classic' },
    6: { id: 6, name: 'Royal Oltin Parda', price: 680000, image: '👑', category: 'luxury' },
    7: { id: 7, name: 'Tungi Ko\'k Parda', price: 320000, image: '🌙', category: 'modern' },
    8: { id: 8, name: 'Premium Karniz', price: 150000, image: '📏', category: 'accessories' },
    9: { id: 9, name: 'Eco Yashil Parda', price: 380000, image: '🍃', category: 'modern' }
};

// ===== UTILITY FUNCTIONS =====

// Load partial HTML files (header, footer)
function loadPartial(elementId, filePath) {
    fetch(filePath)
        .then(response => response.text())
        .then(data => {
            document.getElementById(elementId).innerHTML = data;
            // Initialize mobile menu after header is loaded
            if (elementId === 'header-placeholder') {
                initializeMobileMenu();
                updateCartCount();
                updateUserMenu();
            }
        })
        .catch(error => {
            console.log('Partial fayl yuklanmadi:', filePath);
            // Fallback content for missing partials
            if (elementId === 'header-placeholder') {
                document.getElementById(elementId).innerHTML = '<header class="header"><div class="container"><h1>Navoi <span class="golden">Curtain</span></h1></div></header>';
            }
        });
}

// Format price with thousand separators
function formatPrice(price) {
    return price.toLocaleString('uz-UZ') + ' so\'m';
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// ===== CART FUNCTIONALITY =====

// Add product to cart
function addToCart(productId, quantity = 1, options = {}) {
    const product = products[productId];
    if (!product) return;

    const existingItem = cart.find(item => 
        item.id === productId && 
        JSON.stringify(item.options) === JSON.stringify(options)
    );

    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            id: productId,
            name: product.name,
            price: product.price,
            image: product.image,
            quantity: quantity,
            options: options
        });
    }

    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    showNotification(`${product.name} savatga qo'shildi!`);
}

// Remove product from cart
function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    updateCartDisplay();
    showNotification('Mahsulot savatdan olib tashlandi', 'error');
}

// Update quantity in cart
function updateQuantity(productId, change) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(productId);
            return;
        }
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartDisplay();
        updateCartCount();
    }
}

// Update quantity from input
function updateQuantityInput(productId, newQuantity) {
    const quantity = parseInt(newQuantity);
    if (quantity <= 0) {
        removeFromCart(productId);
        return;
    }
    
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = quantity;
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartDisplay();
        updateCartCount();
    }
}

// Update cart count in header
function updateCartCount() {
    const cartCountElements = document.querySelectorAll('.cart-count');
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    cartCountElements.forEach(element => {
        if (element) element.textContent = totalItems;
    });
}

// Calculate cart total
function calculateCartTotal() {
    const subtotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    const shipping = subtotal >= 500000 ? 0 : 50000; // Free shipping over 500k
    const discount = 0; // Will be calculated based on promo codes
    return {
        subtotal,
        shipping,
        discount,
        total: subtotal + shipping - discount
    };
}

// ===== PAGE-SPECIFIC FUNCTIONS =====

// Initialize mobile menu
function initializeMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navMobile = document.querySelector('.nav-mobile');
    
    if (mobileMenuBtn && navMobile) {
        mobileMenuBtn.addEventListener('click', function() {
            const isVisible = navMobile.style.display === 'block';
            navMobile.style.display = isVisible ? 'none' : 'block';
        });
    }
}

// Update user menu based on login status
function updateUserMenu() {
    const userDropdown = document.querySelector('.user-dropdown');
    if (userDropdown) {
        if (currentUser) {
            userDropdown.innerHTML = `
                <span style="padding: 0.5rem 1rem; color: var(--primary-gold);">Salom, ${currentUser.firstName}!</span>
                <a href="#" onclick="logout()">Chiqish</a>
            `;
        } else {
            userDropdown.innerHTML = `
                <a href="login.html">Kirish</a>
                <a href="register.html">Ro'yxatdan o'tish</a>
            `;
        }
    }
}

// ===== PRODUCT FILTERING (for products.html) =====
function initializeFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const priceFilter = document.getElementById('priceFilter');
    const sortFilter = document.getElementById('sortFilter');

    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterProducts);
    }
    if (priceFilter) {
        priceFilter.addEventListener('change', filterProducts);
    }
    if (sortFilter) {
        sortFilter.addEventListener('change', filterProducts);
    }

    // Check URL parameters for initial filter
    const urlParams = new URLSearchParams(window.location.search);
    const category = urlParams.get('category');
    if (category && categoryFilter) {
        categoryFilter.value = category;
        filterProducts();
    }
}

function filterProducts() {
    const categoryFilter = document.getElementById('categoryFilter');
    const priceFilter = document.getElementById('priceFilter');
    const sortFilter = document.getElementById('sortFilter');
    const productCards = document.querySelectorAll('.product-card');
    const noResults = document.getElementById('noResults');

    let visibleCount = 0;

    productCards.forEach(card => {
        let show = true;

        // Category filter
        const cardCategory = card.getAttribute('data-category');
        const selectedCategory = categoryFilter ? categoryFilter.value : '';
        if (selectedCategory && cardCategory !== selectedCategory) {
            show = false;
        }

        // Price filter
        const cardPrice = parseInt(card.getAttribute('data-price'));
        const selectedPriceRange = priceFilter ? priceFilter.value : '';
        if (selectedPriceRange) {
            const [min, max] = selectedPriceRange.split('-').map(p => parseInt(p.replace('+', '')));
            if (selectedPriceRange.includes('+')) {
                if (cardPrice < min) show = false;
            } else {
                if (cardPrice < min || cardPrice > max) show = false;
            }
        }

        card.style.display = show ? 'block' : 'none';
        if (show) visibleCount++;
    });

    // Show/hide no results message
    if (noResults) {
        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    // Apply sorting
    if (sortFilter && sortFilter.value) {
        sortProducts(sortFilter.value);
    }
}

function sortProducts(sortBy) {
    const productsGrid = document.getElementById('productsGrid');
    if (!productsGrid) return;

    const productCards = Array.from(productsGrid.querySelectorAll('.product-card:not([style*="display: none"])'));
    
    productCards.sort((a, b) => {
        const priceA = parseInt(a.getAttribute('data-price'));
        const priceB = parseInt(b.getAttribute('data-price'));
        
        switch (sortBy) {
            case 'price-low':
                return priceA - priceB;
            case 'price-high':
                return priceB - priceA;
            case 'newest':
            case 'popular':
            default:
                return 0; // Keep original order
        }
    });

    // Re-append sorted elements
    productCards.forEach(card => {
        productsGrid.appendChild(card);
    });
}

// ===== PRODUCT DETAIL FUNCTIONALITY =====
function initializeProductDetail() {
    // Initialize image gallery
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.getElementById('mainImage');
    
    if (thumbnails && mainImage) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                // Remove active class from all thumbnails
                thumbnails.forEach(t => t.classList.remove('active'));
                // Add active class to clicked thumbnail
                this.classList.add('active');
                // Update main image
                const newImage = this.getAttribute('data-image');
                mainImage.textContent = newImage;
            });
        });
    }

    // Initialize option buttons
    const optionButtons = document.querySelectorAll('.option-btn');
    optionButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from siblings
            const siblings = this.parentElement.querySelectorAll('.option-btn');
            siblings.forEach(sibling => sibling.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // Update price based on selected options
            updateDetailPrice();
        });
    });

    // Initialize quantity controls
    updateDetailPrice();
}

function changeQuantity(change) {
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        let newValue = parseInt(quantityInput.value) + change;
        if (newValue < 1) newValue = 1;
        if (newValue > 10) newValue = 10;
        quantityInput.value = newValue;
        updateDetailPrice();
    }
}

function updateDetailPrice() {
    const quantityInput = document.getElementById('quantity');
    const totalPriceElement = document.getElementById('totalPrice');
    const basePrice = 350000; // This would come from backend in real app
    
    if (quantityInput && totalPriceElement) {
        const quantity = parseInt(quantityInput.value) || 1;
        const total = basePrice * quantity;
        totalPriceElement.textContent = formatPrice(total);
    }
}

function addToCartDetail() {
    // Get selected options
    const selectedSize = document.querySelector('#sizeOptions .option-btn.active')?.getAttribute('data-size') || '';
    const selectedColor = document.querySelector('#colorOptions .option-btn.active')?.getAttribute('data-color') || '';
    const selectedMaterial = document.querySelector('#materialOptions .option-btn.active')?.getAttribute('data-material') || '';
    const quantity = parseInt(document.getElementById('quantity')?.value) || 1;
    
    const options = {
        size: selectedSize,
        color: selectedColor,
        material: selectedMaterial
    };

    // Get product ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const productId = parseInt(urlParams.get('id')) || 1;
    
    addToCart(productId, quantity, options);
}

// ===== CART PAGE FUNCTIONALITY =====
function updateCartDisplay() {
    const cartContent = document.getElementById('cartContent');
    const emptyCart = document.getElementById('emptyCart');
    const cartItemsList = document.getElementById('cartItemsList');
    const cartItemCount = document.getElementById('cartItemCount');

    if (!cartContent || !emptyCart) return;

    if (cart.length === 0) {
        cartContent.style.display = 'none';
        emptyCart.style.display = 'block';
        return;
    }

    cartContent.style.display = 'block';
    emptyCart.style.display = 'none';

    // Update item count
    if (cartItemCount) {
        cartItemCount.textContent = cart.length;
    }

    // Update cart items list
    if (cartItemsList) {
        cartItemsList.innerHTML = cart.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <div class="cart-item-image">${item.image}</div>
                <div class="cart-item-info">
                    <h4>${item.name}</h4>
                    <p>${Object.values(item.options || {}).filter(v => v).join(' • ')}</p>
                </div>
                <div class="quantity-controls">
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, -1)">-</button>
                    <input type="number" class="quantity-input" value="${item.quantity}" min="1" onchange="updateQuantityInput(${item.id}, this.value)">
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
                </div>
                <div class="cart-item-price">${formatPrice(item.price * item.quantity)}</div>
                <button class="remove-btn" onclick="removeFromCart(${item.id})">🗑️</button>
            </div>
        `).join('');
    }

    // Update totals
    updateCartTotals();
}

function updateCartTotals() {
    const totals = calculateCartTotal();
    
    // Update cart page elements
    const subtotalElement = document.getElementById('subtotal');
    const shippingElement = document.getElementById('shipping');
    const totalElement = document.getElementById('total');
    
    if (subtotalElement) subtotalElement.textContent = formatPrice(totals.subtotal);
    if (shippingElement) {
        shippingElement.textContent = totals.shipping === 0 ? 'Bepul' : formatPrice(totals.shipping);
    }
    if (totalElement) totalElement.textContent = formatPrice(totals.total);
    
    // Update checkout page elements
    const orderSubtotal = document.getElementById('orderSubtotal');
    const orderShipping = document.getElementById('orderShipping');
    const orderTotal = document.getElementById('orderTotal');
    
    if (orderSubtotal) orderSubtotal.textContent = formatPrice(totals.subtotal);
    if (orderShipping) {
        orderShipping.textContent = totals.shipping === 0 ? 'Bepul' : formatPrice(totals.shipping);
    }
    if (orderTotal) orderTotal.textContent = formatPrice(totals.total);
}

// Apply promo code
function applyPromoCode() {
    const promoCodeInput = document.getElementById('promoCode');
    const promoMessage = document.getElementById('promoMessage');
    
    if (!promoCodeInput || !promoMessage) return;
    
    const code = promoCodeInput.value.trim().toUpperCase();
    
    // Demo promo codes
    const promoCodes = {
        'NAVOI15': { discount: 0.15, description: '15% chegirma' },
        'YANGI10': { discount: 0.10, description: '10% chegirma yangi mijozlar uchun' },
        'BEPUL': { discount: 0, freeShipping: true, description: 'Bepul yetkazib berish' }
    };
    
    promoMessage.style.display = 'block';
    
    if (promoCodes[code]) {
        const promo = promoCodes[code];
        promoMessage.className = 'alert alert-success';
        promoMessage.textContent = `✅ Chegirma kodi qo'llandi: ${promo.description}`;
        
        // Apply discount (this would integrate with backend in real app)
        updateCartTotals();
    } else {
        promoMessage.className = 'alert alert-error';
        promoMessage.textContent = '❌ Noto\'g\'ri chegirma kodi';
    }
}

// ===== AUTHENTICATION =====

// Initialize login form
function initializeLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(loginForm);
        const username = formData.get('username');
        const password = formData.get('password');
        
        // Demo login (this would connect to backend in real app)
        if (username && password) {
            // Simulate successful login
            const user = {
                id: 1,
                firstName: 'Demo',
                lastName: 'User',
                email: username.includes('@') ? username : 'demo@email.com',
                phone: username.includes('@') ? '+998901234567' : username
            };
            
            currentUser = user;
            localStorage.setItem('currentUser', JSON.stringify(user));
            
            document.getElementById('loginSuccess').style.display = 'block';
            document.getElementById('loginError').style.display = 'none';
            
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
        } else {
            document.getElementById('loginError').style.display = 'block';
            document.getElementById('loginSuccess').style.display = 'none';
        }
    });
}

// Initialize register form
function initializeRegisterForm() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;

    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(registerForm);
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');
        
        if (password !== confirmPassword) {
            document.getElementById('registerError').textContent = '❌ Parollar mos kelmaydi';
            document.getElementById('registerError').style.display = 'block';
            return;
        }
        
        // Demo registration (this would connect to backend in real app)
        document.getElementById('registerSuccess').style.display = 'block';
        document.getElementById('registerError').style.display = 'none';
        
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
    });
}

// Logout function
function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    updateUserMenu();
    showNotification('Tizimdan chiqdingiz');
    window.location.href = 'index.html';
}

// ===== CHECKOUT FUNCTIONALITY =====
function initializeCheckout() {
    // Update order summary with cart items
    updateOrderSummary();
    
    // Initialize delivery and payment option styling
    initializeCheckoutOptions();
    
    // Initialize checkout form
    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processCheckout();
        });
    }
}

function updateOrderSummary() {
    const orderItems = document.getElementById('orderItems');
    if (!orderItems || cart.length === 0) return;

    orderItems.innerHTML = cart.map(item => `
        <div class="order-item">
            <div class="order-item-info">
                <h5>${item.name}</h5>
                <p>Miqdor: ${item.quantity} x ${formatPrice(item.price)}</p>
            </div>
            <div class="order-item-price">${formatPrice(item.price * item.quantity)}</div>
        </div>
    `).join('');
    
    updateCartTotals();
}

function initializeCheckoutOptions() {
    // Style delivery options
    const deliveryOptions = document.querySelectorAll('.delivery-option');
    deliveryOptions.forEach(option => {
        const radio = option.querySelector('input[type="radio"]');
        radio.addEventListener('change', function() {
            // Remove active styling from all options
            deliveryOptions.forEach(opt => {
                opt.style.borderColor = 'var(--border-light)';
                opt.style.background = 'var(--white)';
            });
            
            // Add active styling to selected option
            if (this.checked) {
                option.style.borderColor = 'var(--primary-gold)';
                option.style.background = 'var(--light-beige)';
            }
            
            // Update shipping cost
            updateShippingCost(this.value);
        });
    });

    // Style payment options
    const paymentOptions = document.querySelectorAll('.payment-option');
    paymentOptions.forEach(option => {
        const radio = option.querySelector('input[type="radio"]');
        radio.addEventListener('change', function() {
            // Remove active styling from all options
            paymentOptions.forEach(opt => {
                opt.style.borderColor = 'var(--border-light)';
                opt.style.background = 'var(--white)';
            });
            
            // Add active styling to selected option
            if (this.checked) {
                option.style.borderColor = 'var(--primary-gold)';
                option.style.background = 'var(--light-beige)';
            }
        });
    });
}

function updateShippingCost(deliveryType) {
    // This function would update shipping cost based on delivery type
    // For demo purposes, we'll just update the display
    updateCartTotals();
}

function processCheckout() {
    // This would send order data to backend in real app
    showNotification('Buyurtma muvaffaqiyatli qabul qilindi!');
    
    // Clear cart
    cart = [];
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // Redirect to success page or home
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 2000);
}

// ===== CONTACT PAGE FUNCTIONALITY =====
function initializeContactPage() {
    // Initialize FAQ toggles
    const faqQuestions = document.querySelectorAll('.faq-question');
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const answer = this.nextElementSibling;
            const icon = this.querySelector('.faq-icon');
            
            if (answer.style.display === 'block') {
                answer.style.display = 'none';
                icon.textContent = '+';
            } else {
                // Close all other FAQ items
                faqQuestions.forEach(q => {
                    const a = q.nextElementSibling;
                    const i = q.querySelector('.faq-icon');
                    a.style.display = 'none';
                    i.textContent = '+';
                });
                
                // Open clicked item
                answer.style.display = 'block';
                icon.textContent = '-';
            }
        });
    });

    // Initialize contact form
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Demo form submission
            document.getElementById('contactSuccess').style.display = 'block';
            contactForm.reset();
            
            // Scroll to success message
            document.getElementById('contactSuccess').scrollIntoView({ behavior: 'smooth' });
        });
    }
}

// ===== SEARCH FUNCTIONALITY =====
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');
    
    if (searchInput && searchBtn) {
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
}

function performSearch() {
    const searchInput = document.querySelector('.search-input');
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.trim();
    if (searchTerm) {
        // Redirect to products page with search parameter
        window.location.href = `products.html?search=${encodeURIComponent(searchTerm)}`;
    }
}

// ===== SMOOTH SCROLL FUNCTIONALITY =====
function initializeSmoothScroll() {
    const scrollLinks = document.querySelectorAll('.scroll-link');
    scrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ===== INITIALIZE ON LOAD =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize common functionality
    initializeSearch();
    initializeSmoothScroll();
    
    // Update cart count on all pages
    updateCartCount();
});