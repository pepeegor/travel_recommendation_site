// Глобальные обработчики событий
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
    
});

// Инициализация компонентов
function initializeComponents() {
    initializeToasts();
    initializeDropdowns();
    checkAuthStatus();
}

// Инициализация тостов
function initializeToasts() {
    const toastElList = document.querySelectorAll('.toast');
    toastElList.forEach(toastEl => new bootstrap.Toast(toastEl));
}

// Инициализация выпадающих меню
function initializeDropdowns() {
    const dropdownElList = document.querySelectorAll('.dropdown-toggle');
    dropdownElList.forEach(dropdownEl => new bootstrap.Dropdown(dropdownEl));
}

// Проверка статуса авторизации
async function checkAuthStatus() {
    try {
        const response = await fetch('/auth/me', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            handleUnauthenticated();
            return false;
        }

        const userData = await response.json();
        handleAuthenticated(userData);
        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        handleUnauthenticated();
        return false;
    }
}

// Обработка неавторизованного состояния
function handleUnauthenticated() {
    document.querySelectorAll('.auth-required').forEach(el => {
        el.style.display = 'none';
    });
    document.querySelectorAll('.guest-only').forEach(el => {
        el.style.display = 'block';
    });
}

// Обработка авторизованного состояния
function handleAuthenticated(user) {
    document.querySelectorAll('.auth-required').forEach(el => {
        el.style.display = 'block';
    });
    document.querySelectorAll('.guest-only').forEach(el => {
        el.style.display = 'none';
    });

    // Обновление пользовательской информации в UI
    const userNameElements = document.querySelectorAll('.user-name');
    userNameElements.forEach(el => {
        el.textContent = user.username;
    });
}

// Обработчик выхода
async function handleLogout(event) {
    event.preventDefault();
    
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            showNotification('Вы успешно вышли из системы', 'success');
            setTimeout(() => {
                window.location.href = '/pages/';
            }, 1000);
        } else {
            throw new Error('Ошибка при выходе из системы');
        }
    } catch (error) {
        console.error('Logout failed:', error);
        showNotification('Произошла ошибка при выходе из системы', 'danger');
    }
}

// Показ уведомлений
function showNotification(message, type = 'info') {
    const toast = document.getElementById('notificationToast');
    if (toast) {
        const toastBody = toast.querySelector('.toast-body');
        toastBody.textContent = message;
        
        // Удаление предыдущих классов типов
        toast.classList.remove('bg-success', 'bg-danger', 'bg-info', 'bg-warning');
        
        // Добавление соответствующего класса
        switch (type) {
            case 'success':
                toast.classList.add('bg-success');
                break;
            case 'danger':
                toast.classList.add('bg-danger');
                break;
            case 'warning':
                toast.classList.add('bg-warning');
                break;
            default:
                toast.classList.add('bg-info');
        }

        const bsToast = bootstrap.Toast.getOrCreateInstance(toast);
        bsToast.show();
    }
}

// Обработчик ошибок fetch
async function handleFetchResponse(response) {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || 'Произошла ошибка';
        
        if (response.status === 401) {
            window.location.href = '/pages/login';
            throw new Error('Необходима авторизация');
        }
        
        throw new Error(errorMessage);
    }
    return response;
}

// Вспомогательная функция для API запросов
async function fetchApi(url, options = {}) {
    const defaultOptions = {
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    };

    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        await handleFetchResponse(response);
        return await response.json();
    } catch (error) {
        showNotification(error.message, 'danger');
        throw error;
    }
}

// Функция для валидации форм
function validateForm(form) {
    const invalidElements = form.querySelectorAll(':invalid');
    if (invalidElements.length > 0) {
        invalidElements.forEach(element => {
            element.classList.add('is-invalid');
        });
        return false;
    }
    return true;
}

// Очистка ошибок валидации при вводе
document.addEventListener('input', function(event) {
    const input = event.target;
    if (input.classList.contains('is-invalid')) {
        input.classList.remove('is-invalid');
    }
});

// Обработчик ошибок Promise
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showNotification('Произошла непредвиденная ошибка', 'danger');
});



// Экспорт функций для использования в других модулях
window.app = {
    showNotification,
    fetchApi,
    validateForm,
    checkAuthStatus,
    handleLogout
};

