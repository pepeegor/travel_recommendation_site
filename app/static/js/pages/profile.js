document.addEventListener('DOMContentLoaded', function () {
    const editProfileForm = document.getElementById('editProfileForm');
    const editProfileModal = document.getElementById('editProfileModal');
    const createReviewModal = document.getElementById('createReviewModal'); // Получаем модальное окно для создания отзыва

    if (editProfileForm) {
        editProfileForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            if (!app.validateForm(editProfileForm)) {
                return;
            }

            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await app.fetchApi('/auth/me', {
                    method: 'PUT',
                    body: JSON.stringify({ username, email, password }),
                });

                app.showNotification('Профиль успешно обновлен', 'success');

                // Обновляем информацию о пользователе в UI
                document.querySelector('.user-name').textContent = response.username; 
                document.querySelector('.user-email').textContent = response.email; 

                // Закрываем модальное окно после успешного обновления
                const modal = bootstrap.Modal.getInstance(editProfileModal);
                modal.hide();
            } catch (error) {
                // Обработка ошибок уже выполняется в fetchApi
            }
        });
    }

    // Обработчик события для формы создания отзыва
    document.getElementById('createReviewForm').addEventListener('submit', async function(event) {
        event.preventDefault();

        if (!app.validateForm(event.target)) {
            return;
        }

        const destinationId = document.getElementById('destination').value;
        const rating = parseInt(document.getElementById('rating').value);
        const comment = document.getElementById('comment').value;

        try {
            const response = await app.fetchApi('/reviews', {
                method: 'POST',
                body: JSON.stringify({ destination_id: destinationId, rating, comment }),
            });

            app.showNotification('Отзыв успешно создан', 'success');

            // Обновляем список отзывов
            loadUserReviews(); 

            // Закрываем модальное окно
            const modal = bootstrap.Modal.getInstance(createReviewModal);
            modal.hide();
        } catch (error) {
            // Обработка ошибок уже выполняется в fetchApi
        }
    });

    // Загрузка отзывов пользователя
    loadUserReviews();
});

async function loadUserReviews() {
    try {
        const response = await app.fetchApi('/reviews/user');
        const reviewsContainer = document.getElementById('reviews');
        
        if (response.total === 0) {
            reviewsContainer.innerHTML = '<p>Вы еще не оставили ни одного отзыва.</p>';
            return;
        }

        reviewsContainer.innerHTML = ''; // Очищаем контейнер перед добавлением отзывов

        response.reviews.forEach(review => {
            const reviewElement = `
            <div class="card mb-3">
                <div class="card-header">
                ${review.destination.name}, ${review.destination.country} 
                <span class="float-end">
                    <i class="bi bi-star-fill"></i> Оценка: ${review.rating} 
                </span>
                </div>
                <div class="card-body">
                <p>${review.comment}</p>
                <p class="text-muted">Дата: ${new Date(review.created_at).toLocaleDateString()}</p>
                <a href="/pages/reviews/${review.id}" class="btn btn-primary">Подробнее</a> 
                </div>
            </div>
            `;
            reviewsContainer.innerHTML += reviewElement; 
        });
    } catch (error) {
        // Обработка ошибок уже выполняется в fetchApi
    }
}