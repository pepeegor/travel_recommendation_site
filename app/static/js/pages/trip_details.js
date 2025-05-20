const tripDetailsElement = document.getElementById('tripDetails'); 
const tripId = tripDetailsElement ? tripDetailsElement.dataset.tripId : null;

if (!tripId) {
  console.error('Не найден tripId!');
} else {
  document.getElementById('updateTripForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Предотвращаем стандартную отправку формы

    if (!validateForm(event.target)) {  // Вызываем validateForm
        app.showNotification('Пожалуйста, проверьте правильность заполнения формы', 'warning');
        return;
    }

    const budget = parseFloat(document.getElementById('budget').value);
    const status = document.getElementById('status')?.value;

    if (isNaN(budget)) {
      app.showNotification('Некорректные данные в форме', 'warning');
      return;
    }

    try {
        // Используем tripsAPI.update, передаем budget и status
        const updatedTrip = await tripsAPI.update(tripId, { 
            budget, 
            status 
        }); 

        app.showNotification('Путешествие успешно обновлено!', 'success');
    } catch (error) {
        console.error('Ошибка при обновлении путешествия:', error);
        app.showNotification('Ошибка при обновлении путешествия', 'danger');
    }
  });

  document.getElementById('deleteTripButton').addEventListener('click', async function() {
      if (confirm('Вы уверены, что хотите удалить это путешествие?')) {
          try {
              await tripsAPI.delete(tripId);
              app.showNotification('Путешествие успешно удалено!', 'success');
              // Перенаправление на страницу списка путешествий
              window.location.href = '/pages/trips'; 
          } catch (error) {
              console.error('Ошибка при удалении путешествия:', error);
              app.showNotification('Ошибка при удалении путешествия', 'danger');
          }
      }
  });
} 
