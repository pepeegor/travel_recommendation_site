// review_details.js
const reviewDetailsElement = document.getElementById('reviewDetails');
const reviewId = reviewDetailsElement ? reviewDetailsElement.dataset.reviewId : null;

if (!reviewId) {
    console.error('Не найден reviewId!');
} else {
    document.getElementById('updateReviewForm').addEventListener('submit', async function (event) {
        event.preventDefault();

        if (!app.validateForm(event.target)) {
            app.showNotification('Пожалуйста, проверьте правильность заполнения формы', 'warning');
            return;
        }

        const rating = parseInt(document.getElementById('rating').value);
        const comment = document.getElementById('comment').value;

        if (isNaN(rating) || rating < 1 || rating > 5) {
            app.showNotification('Некорректные данные в форме', 'warning');
            return;
        }

        try {
            // Используем reviewsAPI.update, передаем rating и comment (необходимо создать reviewsAPI)
            const updatedReview = await reviewsAPI.update(reviewId, {
                rating,
                comment
            });

            app.showNotification('Отзыв успешно обновлен!', 'success');
        } catch (error) {
            console.error('Ошибка при обновлении отзыва:', error);
            app.showNotification('Ошибка при обновлении отзыва', 'danger');
        }
    });

    document.getElementById('deleteReviewButton').addEventListener('click', async function () {
        if (confirm('Вы уверены, что хотите удалить этот отзыв?')) {
            try {
                // Используем reviewsAPI.delete (необходимо создать reviewsAPI)
                await reviewsAPI.delete(reviewId);
                app.showNotification('Отзыв успешно удален!', 'success');
                // Перенаправление на страницу профиля пользователя
                window.location.href = '/pages/profile';
            } catch (error) {
                console.error('Ошибка при удалении отзыва:', error);
                app.showNotification('Ошибка при удалении отзыва', 'danger');
            }
        }
    });
}