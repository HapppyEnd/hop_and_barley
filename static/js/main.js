// --- Product Page Quantity Update Functions ---
window.changeQuantity = function(change, maxStock, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const quantityInput = document.getElementById('quantity');
    
    if (!quantityInput) {
        return;
    }
    
    let currentQuantity = parseInt(quantityInput.value) || 1;
    let newQuantity = currentQuantity + change;
    
    if (newQuantity < 1) {
        newQuantity = 1;
    } else if (newQuantity > maxStock) {
        newQuantity = maxStock;
    }
    
    quantityInput.value = newQuantity;
};

window.updateQuantityDirect = function(input, maxStock) {
    let newQuantity = parseInt(input.value) || 1;
    
    if (newQuantity < 1) {
        newQuantity = 1;
    } else if (newQuantity > maxStock) {
        newQuantity = maxStock;
    }
    
    input.value = newQuantity;
    
    const hiddenInput = input.parentNode.querySelector('.quantity-input');
    if (hiddenInput) {
        hiddenInput.value = newQuantity;
    }
    
    const form = input.closest('form');
    if (form) {
        setTimeout(() => {
            form.submit();
        }, 100);
    }
};

document.addEventListener('DOMContentLoaded', function() {


    // --- Logic for Product List Page (Filtering, Sorting, Search) ---
    const homePageContent = document.querySelector('.main-content-grid');
    if (homePageContent) {
        const mainFilterForm = document.getElementById('main-filter-form');
        const sortInput = document.getElementById('sort-input');
        const searchField = document.getElementById('search-field');
        
        // Отладка - проверяем, что все элементы найдены
        console.log('Elements found:', {
            mainFilterForm: !!mainFilterForm,
            sortInput: !!sortInput,
            searchField: !!searchField
        });
        
        if (mainFilterForm) {
            console.log('Form details:', {
                id: mainFilterForm.id,
                action: mainFilterForm.action,
                method: mainFilterForm.method
            });
        }

        // 1. Sort Options Logic
        const sortButtons = document.querySelectorAll('.sort-options .sort-button');
        console.log('Found sort buttons:', sortButtons.length); // Отладка
        
        sortButtons.forEach(button => {
            console.log('Button data-sort:', button.dataset.sort); // Отладка
            
            button.addEventListener('click', function() {
                const sortValue = this.dataset.sort;
                console.log('Sort button clicked:', sortValue); // Отладка
                
                if (sortInput) {
                    sortInput.value = sortValue;
                    console.log('Sort input value set to:', sortInput.value); // Отладка
                } else {
                    console.error('Sort input not found!'); // Отладка
                }

                sortButtons.forEach(btn => btn.classList.remove('active-sort'));
                this.classList.add('active-sort');

                // Submit the main filter form
                if (mainFilterForm) {
                    console.log('Submitting form with sort:', sortValue); // Отладка
                    console.log('Form action:', mainFilterForm.action); // Отладка
                    console.log('Form method:', mainFilterForm.method); // Отладка
                    console.log('Form data before submit:', new FormData(mainFilterForm)); // Отладка
                    mainFilterForm.submit();
                } else {
                    console.error('Main filter form not found!'); // Отладка
                }
            });
        });

        // 2. Search functionality - теперь работает через форму
        if (searchField) {
            // Поиск по Enter
            searchField.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    if (mainFilterForm) {
                        mainFilterForm.submit();
                    }
                }
            });
        }

        // 3. Filter Logic (Keywords and Checkboxes)
        const keywordsList = document.getElementById('keywords-list');
        const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]');

        if (keywordsList && checkboxes.length > 0) {
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const keyword = this.dataset.keyword;
                    const value = this.value;

                    if (this.checked) {
                        if (!document.querySelector(`.keyword-tag[data-keyword="${value}"]`)) {
                            const newTag = document.createElement('span');
                            newTag.className = 'keyword-tag';
                            newTag.setAttribute('data-keyword', value);
                            newTag.innerHTML = `${keyword} <i class="fa-solid fa-xmark remove-keyword-icon"></i>`;
                            keywordsList.appendChild(newTag);
                        }
                    } else {
                        const tagToRemove = document.querySelector(`.keyword-tag[data-keyword="${value}"]`);
                        if (tagToRemove) {
                            tagToRemove.remove();
                        }
                    }

                    // НЕ отправляем форму сразу - ждем нажатия кнопки "Apply Filters"
                    // filterForm.submit();
                });
            });

            keywordsList.addEventListener('click', function(event) {
                if (event.target.closest('.remove-keyword-icon')) {
                    event.preventDefault();
                    const keywordTag = event.target.closest('.keyword-tag');
                    const keywordValue = keywordTag.dataset.keyword;

                    // Uncheck corresponding checkbox
                    const checkbox = document.querySelector(`.checkbox-group input[value="${keywordValue}"]`);
                    if (checkbox) {
                        checkbox.checked = false;
                        // НЕ отправляем форму сразу - ждем нажатия кнопки "Apply Filters"
                        // filterForm.submit();
                    }

                    keywordTag.remove();
                }
            });
        }

        // 4. Clear all filters button
        const clearFiltersBtn = document.createElement('button');
        clearFiltersBtn.textContent = 'Clear All Filters';
        clearFiltersBtn.className = 'button button--secondary';
        clearFiltersBtn.style.marginTop = '16px';
        clearFiltersBtn.style.width = '100%';
        clearFiltersBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = window.location.pathname;
        });

        const filterButton = mainFilterForm.querySelector('.filter-button');
        if (filterButton) {
            filterButton.parentNode.insertBefore(clearFiltersBtn, filterButton.nextSibling);
        }
    }

    // --- Messages Auto-hide ---
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000); // Hide after 5 seconds
    });

    // --- Logic for Product Detail Pages (product-*.html) ---
    const productPageContent = document.querySelector('.page-product');
    if (productPageContent) {
        // Accordion
        const accordionTitle = document.querySelector('.accordion-title');
        if (accordionTitle) {
            accordionTitle.addEventListener('click', function() {
                const accordionItem = this.closest('.accordion-item');
                const accordionContent = accordionItem.querySelector('.accordion-content');
                const accordionIcon = this.querySelector('.accordion-icon');
                
                accordionItem.classList.toggle('active');
                
                if (accordionItem.classList.contains('active')) {
                    accordionContent.style.display = 'block';
                    accordionIcon.style.transform = 'rotate(180deg)';
                } else {
                    accordionContent.style.display = 'none';
                    accordionIcon.style.transform = 'rotate(0deg)';
                }
            });
        }

        // "Add to Cart" Button and Counter
        const cartControls = document.querySelector('.cart-controls');
        if (cartControls) {
            const addToCartBtn = cartControls.querySelector('#add-to-cart-btn');
            const quantityCounter = cartControls.querySelector('#quantity-counter');
            
            // Only proceed if quantityCounter exists
            if (quantityCounter) {
                const decreaseBtn = quantityCounter.querySelector('[data-action="decrease"]');
                const increaseBtn = quantityCounter.querySelector('[data-action="increase"]');
                const quantityValueSpan = quantityCounter.querySelector('.quantity-value');
                let quantity = 0;

                function updateView() {
                    if (quantity === 0) {
                        addToCartBtn.classList.remove('is-hidden');
                        quantityCounter.classList.add('is-hidden');
                    } else {
                        addToCartBtn.classList.add('is-hidden');
                        quantityCounter.classList.remove('is-hidden');
                        quantityValueSpan.textContent = `${quantity} in cart`;
                    }
                }

                addToCartBtn.addEventListener('click', function() {
                    quantity = 1;
                    updateView();
                });

                decreaseBtn.addEventListener('click', function() {
                    if (quantity > 0) {
                        quantity--;
                        updateView();
                    }
                });

                increaseBtn.addEventListener('click', function() {
                    quantity++;
                    updateView();
                });

                updateView();
            }
        }


    }

    // --- Logic for Cart Page (cart.html) ---
    const cartPageContent = document.querySelector('.cart-page-wrapper');
    if (cartPageContent) {
        const cartItemsList = document.getElementById('cart-items-list');
        const cartTotalPriceElem = document.getElementById('cart-total-price');

        function updateCartTotal() {
            let total = 0;
            document.querySelectorAll('.cart-item').forEach(item => {
                const priceText = item.querySelector('[data-item-total-price]').textContent;
                if (priceText) {
                    total += parseFloat(priceText.replace('$', ''));
                }
            });
            if (cartTotalPriceElem) cartTotalPriceElem.textContent = `$${total.toFixed(2)}`;
        }

        if (cartItemsList) {
            cartItemsList.addEventListener('click', function(event) {
                const cartItem = event.target.closest('.cart-item');
                if (!cartItem) return;

                const quantityElem = cartItem.querySelector('.quantity-value-cart');
                const itemTotalElem = cartItem.querySelector('[data-item-total-price]');
                const basePrice = parseFloat(cartItem.dataset.price);
                let quantity = parseInt(quantityElem.textContent);

                if (event.target.closest('[data-action="increase"]')) {
                    quantity++;
                } else if (event.target.closest('[data-action="decrease"]')) {
                    quantity = quantity > 1 ? quantity - 1 : 0;
                }

                if (event.target.closest('[data-action="remove"]') || quantity === 0) {
                    cartItem.remove();
                } else {
                    quantityElem.textContent = quantity;
                    itemTotalElem.textContent = `$${(basePrice * quantity).toFixed(2)}`;
                }

                updateCartTotal();
            });
        }
        updateCartTotal();
    }

    // --- URL Parameter Handling ---
    function updateURLParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const searchQuery = urlParams.get('search');
        const sortBy = urlParams.get('sort');
        const categories = urlParams.getAll('category');

        // Update search field
        if (searchQuery && document.getElementById('search-field')) {
            document.getElementById('search-field').value = searchQuery;
        }

        // Update sort buttons
        if (sortBy && document.querySelector(`.sort-button[data-sort="${sortBy}"]`)) {
            document.querySelectorAll('.sort-button').forEach(btn => btn.classList.remove('active-sort'));
            document.querySelector(`.sort-button[data-sort="${sortBy}"]`).classList.add('active-sort');
        }

        // Update checkboxes
        categories.forEach(categoryId => {
            const checkbox = document.querySelector(`.checkbox-group input[value="${categoryId}"]`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
    }

         updateURLParams();
 
    // --- Cart Quantity Update Functions ---
    window.updateQuantity = function(button, change, maxStock) {
        const quantityInput = button.parentNode.querySelector('.quantity-input-cart');
        const hiddenInput = button.parentNode.querySelector('.quantity-input');
        
        if (!quantityInput || !hiddenInput) {
            return;
        }
        
        let currentQuantity = parseInt(quantityInput.value) || 0;
        const newQuantity = currentQuantity + change;
        
        if (newQuantity < 1) {
            const cartItem = button.closest('.cart-item');
            if (cartItem) {
                const removeForm = cartItem.querySelector('form[action*="cart/remove"]');
                if (removeForm) {
                    removeForm.submit();
                }
            }
            return;
        }
        
        if (newQuantity > maxStock) {
            currentQuantity = maxStock;
        } else {
            currentQuantity = newQuantity;
        }
        
        quantityInput.value = currentQuantity;
        hiddenInput.value = currentQuantity;
        
        setTimeout(() => {
            const form = button.closest('form');
            if (form) {
                form.submit();
            }
        }, 100);
    };





    // --- Cart Button Event Listeners ---
    const quantityButtons = document.querySelectorAll('.quantity-btn-cart');
    quantityButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            this.disabled = true;
            setTimeout(() => {
                this.disabled = false;
            }, 500);
        });
    });

    // --- Star Rating Logic ---
    const starRating = document.querySelector('.star-rating');
    if (starRating) {
        const ratingInput = document.querySelector('input[name="rating"]');
        const stars = starRating.querySelectorAll('i');

        // Initialize with existing rating if any
        const currentRating = parseInt(ratingInput.value) || 0;
        if (currentRating > 0) {
            stars.forEach((s, i) => {
                if (i < currentRating) {
                    s.classList.add('active');
                    s.style.color = '#ffc107';
                }
            });
        }

        stars.forEach((star, index) => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                ratingInput.value = rating;
                
                // Update visual state
                stars.forEach((s, i) => {
                    if (i < rating) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });

            star.addEventListener('mouseenter', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                stars.forEach((s, i) => {
                    if (i < rating) {
                        s.style.color = '#ffc107';
                    } else {
                        s.style.color = '#ddd';
                    }
                });
            });
        });

        starRating.addEventListener('mouseleave', function() {
            const currentRating = parseInt(ratingInput.value) || 0;
            stars.forEach((s, i) => {
                if (i < currentRating) {
                    s.style.color = '#ffc107';
                } else {
                    s.style.color = '#ddd';
                }
            });
        });
    }

    // --- Account Page Tab Switching ---
    const accountPageContent = document.querySelector('.account-page-wrapper');
    if (accountPageContent) {
        const tabs = document.querySelectorAll('.account-tab');
        const tabPanes = document.querySelectorAll('.tab-pane');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const targetId = this.getAttribute('data-tab-target');
                
                // Remove active class from all tabs and panes
                tabs.forEach(t => t.classList.remove('active'));
                tabPanes.forEach(p => p.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding pane
                this.classList.add('active');
                const targetPane = document.querySelector(targetId);
                if (targetPane) {
                    targetPane.classList.add('active');
                }
            });
        });
    }

    // --- Checkout Page Logic ---
    const checkoutPageContent = document.querySelector('.checkout-page-wrapper');
    if (checkoutPageContent) {
        // Address autofill functionality
        const autofillButton = document.getElementById('autofill-address');
        const addressTextarea = document.getElementById('shipping_address');
        
        if (autofillButton && addressTextarea) {
            autofillButton.addEventListener('click', function() {
                // Get user's saved address data
                const userCity = autofillButton.dataset.city || '';
                const userAddress = autofillButton.dataset.address || '';
                
                // Combine city and address
                let fullAddress = '';
                if (userAddress) {
                    fullAddress = userAddress;
                }
                if (userCity) {
                    if (fullAddress) {
                        fullAddress += ', ' + userCity;
                    } else {
                        fullAddress = userCity;
                    }
                }
                
                // Fill the textarea
                if (fullAddress) {
                    addressTextarea.value = fullAddress;
                    // Add visual feedback
                    autofillButton.innerHTML = '<i class="fas fa-check"></i> Address filled!';
                    autofillButton.classList.add('button--success');
                    setTimeout(() => {
                        autofillButton.innerHTML = '<i class="fas fa-map-marker-alt"></i> Use my saved address';
                        autofillButton.classList.remove('button--success');
                    }, 2000);
                }
            });
        }

        // Payment method switching
        const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
        const cardForm = document.getElementById('card-payment-form');
        const cashInfo = document.getElementById('cash-payment-info');
        
        function togglePaymentForms() {
            const selectedMethod = document.querySelector('input[name="payment_method"]:checked').value;
            
            if (selectedMethod === 'card') {
                cardForm.style.display = 'block';
                cashInfo.style.display = 'none';
            } else {
                cardForm.style.display = 'none';
                cashInfo.style.display = 'block';
            }
        }
        
        // Add event listeners to payment method radio buttons
        paymentMethods.forEach(method => {
            method.addEventListener('change', togglePaymentForms);
        });
        
        // Initialize form visibility
        togglePaymentForms();

        // Card number formatting
        const cardNumberInput = document.getElementById('card_number');
        if (cardNumberInput) {
            cardNumberInput.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
                let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
                if (formattedValue.length <= 19) {
                    e.target.value = formattedValue;
                }
            });
        }

        // Expiry date formatting and validation
        const expiryInput = document.getElementById('expiry_date');
        const expiryError = document.getElementById('expiry_error');
        
        if (expiryInput) {
            expiryInput.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length >= 2) {
                    value = value.substring(0, 2) + '/' + value.substring(2, 4);
                }
                e.target.value = value;
                
                // Clear error state when user starts typing
                e.target.classList.remove('error');
                if (expiryError) {
                    expiryError.style.display = 'none';
                }
            });
            
            // Validate on blur
            expiryInput.addEventListener('blur', function(e) {
                const value = e.target.value.trim();
                if (value && value.length === 5) {
                    if (!validateCardExpiry(value)) {
                        e.target.classList.add('error');
                        if (expiryError) {
                            expiryError.style.display = 'block';
                        }
                    } else {
                        e.target.classList.remove('error');
                        if (expiryError) {
                            expiryError.style.display = 'none';
                        }
                    }
                }
            });
        }

        // Card holder formatting (letters, spaces, hyphens, apostrophes only)
        const cardHolderInput = document.getElementById('card_holder');
        if (cardHolderInput) {
            cardHolderInput.addEventListener('input', function(e) {
                e.target.value = e.target.value.replace(/[^a-zA-Z\s\-']/g, '').slice(0, 50);
            });
        }

        // CVV formatting (numbers only, max 3 digits)
        const cvvInput = document.getElementById('cvv');
        if (cvvInput) {
            cvvInput.addEventListener('input', function(e) {
                e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 3);
            });
        }

        function validateCardExpiry(expiryDate) {
            try {
                if (!expiryDate || expiryDate.length !== 5 || expiryDate[2] !== '/') {
                    return false;
                }
                
                const [month, year] = expiryDate.split('/');
                
                if (!/^\d{2}$/.test(month) || !/^\d{2}$/.test(year)) {
                    return false;
                }
                
                const monthNum = parseInt(month);
                const yearNum = parseInt('20' + year);
                
                if (monthNum < 1 || monthNum > 12) {
                    return false;
                }
                
                const currentDate = new Date();
                const currentYear = currentDate.getFullYear();
                const currentMonth = currentDate.getMonth() + 1;
                
                if (yearNum < currentYear || (yearNum === currentYear && monthNum < currentMonth)) {
                    return false;
                }
                
                return true;
            } catch (error) {
                return false;
            }
        }

        const checkoutForm = document.getElementById('checkout-form');
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', function(e) {
                const selectedMethod = document.querySelector('input[name="payment_method"]:checked').value;
                
                if (selectedMethod === 'card') {
                    const cardNumber = document.getElementById('card_number').value;
                    const cardHolder = document.getElementById('card_holder').value;
                    const expiryDate = document.getElementById('expiry_date').value;
                    const cvv = document.getElementById('cvv').value;
                    
                    if (!cardNumber || !cardHolder || !expiryDate || !cvv) {
                        e.preventDefault();
                        alert('Please fill in all card details');
                        return;
                    }
                    
                    const cleanCardNumber = cardNumber.replace(/\s/g, '');
                    if (cleanCardNumber.length < 13 || cleanCardNumber.length > 19) {
                        e.preventDefault();
                        alert('Card number must be between 13 and 19 digits');
                        return;
                    }
                    
                    if (!/^\d+$/.test(cleanCardNumber)) {
                        e.preventDefault();
                        alert('Card number must contain only digits');
                        return;
                    }
                    
                    if (!validateCardExpiry(expiryDate)) {
                        e.preventDefault();
                        alert('Card has expired');
                        return;
                    }
                    
                    if (!/^\d{2}\/\d{2}$/.test(expiryDate)) {
                        e.preventDefault();
                        alert('Invalid expiry date format');
                        return;
                    }
                    
                    if (cvv.length !== 3 || !/^\d{3}$/.test(cvv)) {
                        e.preventDefault();
                        alert('CVV must be exactly 3 digits');
                        return;
                    }
                    
                    // Validate card holder name
                    if (cardHolder.length < 2 || cardHolder.length > 50) {
                        e.preventDefault();
                        alert('Card holder name must be between 2 and 50 characters');
                        return;
                    }
                    
                    if (!/^[a-zA-Z\s\-']+$/.test(cardHolder)) {
                        e.preventDefault();
                        alert('Card holder name can only contain letters, spaces, hyphens, and apostrophes');
                        return;
                    }
                    
                    if (!/[a-zA-Z]/.test(cardHolder)) {
                        e.preventDefault();
                        alert('Card holder name must contain at least one letter');
                        return;
                    }
                }
            });
        }
    }

 
 });