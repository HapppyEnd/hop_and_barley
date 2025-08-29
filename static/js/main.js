document.addEventListener('DOMContentLoaded', function() {

    // --- General logic for all pages (Login/Logout Simulation) ---
    const loginForm = document.getElementById('login-form');
    const logoutButton = document.getElementById('logout-button');

    function checkLoginStatus() {
        if (localStorage.getItem('isLoggedIn') === 'true') {
            document.body.classList.add('user-logged-in');
        } else {
            document.body.classList.remove('user-logged-in');
        }
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem('isLoggedIn');
            window.location.href = 'home.html';
        });
    }
    checkLoginStatus();

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
        sortButtons.forEach(button => {
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

    // --- Logic for Product Detail Pages (product-*.html) ---
    const productPageContent = document.querySelector('.page-product');
    if (productPageContent) {
        // Accordion
        const accordionTitle = document.querySelector('.accordion-title');
        if (accordionTitle) {
            accordionTitle.addEventListener('click', function() {
                this.closest('.accordion-item').classList.toggle('active');
            });
        }

        // "Add to Cart" Button and Counter
        const cartControls = document.querySelector('.cart-controls');
        if (cartControls) {
            const addToCartBtn = cartControls.querySelector('#add-to-cart-btn');
            const quantityCounter = cartControls.querySelector('#quantity-counter');
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
 
 });