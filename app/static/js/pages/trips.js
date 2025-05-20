document.addEventListener('DOMContentLoaded', function() {
    fetchTrips();
});

async function fetchTrips() {
    try {
        const trips = await tripsAPI.getAll();
        console.log('Полученные путешествия:', trips);
        const tripsContainer = document.getElementById('tripsContainer');
        tripsContainer.innerHTML = '';

        if (trips.length === 0) {
            const noTripsMessage = document.createElement('div');
            noTripsMessage.className = 'no-trips-message';
            noTripsMessage.innerHTML = '<p>У вас пока нет путешествий. Начните планировать новое путешествие!</p>';
            tripsContainer.appendChild(noTripsMessage);
        } else {
            // Используем Promise.all для одновременного получения всех направлений
            await Promise.all(trips.map(async (trip) => {
                let destinationName = 'Неизвестное направление';
                if (trip.destination_id) {
                    try {
                        const destination = await destinationsAPI.getById(trip.destination_id);
                        destinationName = destination.name || destinationName;
                    } catch (error) {
                        console.error('Ошибка при получении направления:', error);
                    }
                }

                const tripCard = document.createElement('div');
                tripCard.className = 'col-md-4 trip-card';
                tripCard.innerHTML = `
                    <h2>${destinationName}</h2>
                    <p>Дата начала: ${trip.start_date ? new Date(trip.start_date).toLocaleDateString() : 'Неизвестно'}</p>
                    <p>Дата окончания: ${trip.end_date ? new Date(trip.end_date).toLocaleDateString() : 'Неизвестно'}</p>
                    <p class="trip-details">Бюджет: ${trip.budget || 'Неизвестно'}</p>
                    <p>Статус: ${trip.status === 'planned' ? 'Запланировано' : 
                                trip.status === 'in_progress' ? 'В процессе' : 
                                trip.status === 'completed' ? 'Завершено' : 'Неизвестно'}</p> 
                `;
                const link = document.createElement('a');
                link.href = `/pages/trips/${trip.id}`;
                link.className = 'btn btn-primary';
                link.textContent = 'Подробнее';
                tripCard.appendChild(link);
                tripsContainer.appendChild(tripCard);
            }));
        }
    } catch (error) {
        console.error('Ошибка при получении путешествий:', error);
    }
}