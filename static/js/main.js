// Основные функции для работы с интерфейсом

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие уведомлений через 5 секунд
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Инициализация tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Инициализация popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Функция для добавления в корзину через AJAX
function addToCart(productId, sizeId, quantity = 1) {
    if (!sizeId) {
        alert('Пожалуйста, выберите размер');
        return;
    }
    
    showLoading();
    
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `size=${sizeId}&quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            updateCartCount(data.cart_count);
            showNotification(data.message, 'success');
        } else {
            showNotification(data.message, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showNotification('Произошла ошибка', 'danger');
        console.error('Error:', error);
    });
}

// Функция для обновления количества товара в корзине
function updateCartItem(itemId, quantity) {
    showLoading();
    
    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `quantity=${quantity}`
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    })
    .catch(error => {
        hideLoading();
        showNotification('Произошла ошибка', 'danger');
        console.error('Error:', error);
    });
}

// Функция для удаления товара из корзины
function removeFromCart(itemId) {
    if (!confirm('Удалить товар из корзины?')) {
        return;
    }
    
    showLoading();
    
    fetch(`/cart/remove/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    })
    .catch(error => {
        hideLoading();
        showNotification('Произошла ошибка', 'danger');
        console.error('Error:', error);
    });
}

// Функция для поиска товаров (AJAX)
function searchProducts(query) {
    if (query.length < 3) {
        document.getElementById('searchResults').innerHTML = '';
        return;
    }
    
    fetch(`/search/?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = '';
        
        if (data.results.length > 0) {
            data.results.forEach(product => {
                resultsDiv.innerHTML += `
                    <a href="${product.url}" class="list-group-item list-group-item-action">
                        <div class="d-flex align-items-center">
                            <img src="${product.image}" alt="${product.name}" style="width: 40px; height: 40px; object-fit: cover;" class="me-2">
                            <div>
                                <h6 class="mb-0">${product.name}</h6>
                                <small class="text-primary">${product.price} ₽</small>
                            </div>
                        </div>
                    </a>
                `;
            });
        } else {
            resultsDiv.innerHTML = '<div class="list-group-item">Ничего не найдено</div>';
        }
    })
    .catch(error => console.error('Error:', error));
}

// Функция для получения cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция для обновления счетчика корзины
function updateCartCount(count) {
    const cartBadge = document.querySelector('.badge.bg-danger');
    if (cartBadge) {
        cartBadge.textContent = count;
        if (count === 0) {
            cartBadge.style.display = 'none';
        } else {
            cartBadge.style.display = 'inline';
        }
    }
}

// Функция для показа уведомления
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 3000);
}

// Функция для показа загрузки
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingSpinner';
    loadingDiv.className = 'position-fixed top-50 start-50 translate-middle';
    loadingDiv.style.zIndex = '9999';
    loadingDiv.innerHTML = '<div class="loading-spinner"></div>';
    
    document.body.appendChild(loadingDiv);
}

// Функция для скрытия загрузки
function hideLoading() {
    const loadingDiv = document.getElementById('loadingSpinner');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Валидация форм
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Проверка обязательных полей
        this.querySelectorAll('[required]').forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        // Проверка email
        const emailField = this.querySelector('input[type="email"]');
        if (emailField && emailField.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(emailField.value)) {
                emailField.classList.add('is-invalid');
                isValid = false;
            }
        }
        
        // Проверка телефона
        const phoneField = this.querySelector('input[name="phone"]');
        if (phoneField && phoneField.value) {
            const phoneRegex = /^\+?[\d\s-]{10,}$/;
            if (!phoneRegex.test(phoneField.value)) {
                phoneField.classList.add('is-invalid');
                isValid = false;
            }
        }
        
        if (!isValid) {
            e.preventDefault();
            showNotification('Пожалуйста, заполните все поля правильно', 'warning');
        }
    });
});