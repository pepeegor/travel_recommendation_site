// app/static/js/pages/auth.js

async function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    try {
        if (!validateForm(form)) {
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Регистрация...';
        
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: form.email.value,
                password: form.password.value,
                username: form.username.value
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Ошибка регистрации');
        }

        app.showNotification('Регистрация успешна! Выполните вход.', 'success');
        setTimeout(() => {
            window.location.href = '/pages/login';
        }, 1500);
    } catch (error) {
        app.showNotification(error.message, 'danger');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-person-plus"></i> Зарегистрироваться';
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    try {
        if (!validateForm(form)) {
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Вход...';
        
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: form.email.value,
                password: form.password.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка входа');
        }

        app.showNotification('Вход выполнен успешно!', 'success');
        setTimeout(() => {
            window.location.href = '/pages/';
        }, 1000);
    } catch (error) {
        app.showNotification(error.message, 'danger');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-box-arrow-in-right"></i> Войти';
    }
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('bi-eye', 'bi-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('bi-eye-slash', 'bi-eye');
    }
}

// Экспорт функций
window.auth = {
    handleLogin,
    handleRegister,
    togglePassword
};