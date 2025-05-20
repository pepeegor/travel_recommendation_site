
document.addEventListener('DOMContentLoaded', fetchBookings);

async function fetchBookings() {
    const container = document.getElementById('bookingsContainer');
    const noMsg = document.getElementById('noBookingsMessage');
    container.innerHTML = '';

    try {
        const response = await fetch('/bookings/me', { credentials: 'include' });
        if (!response.ok) throw new Error('Ошибка при загрузке бронирований');
        const data = await response.json();
        const bookings = data.bookings || [];

        if (bookings.length === 0) {
            noMsg.classList.remove('d-none');
            return;
        } else {
            noMsg.classList.add('d-none');
        }

        // Загрузка названий направлений параллельно
        await Promise.all(
            bookings.map(async (b) => {
                let destName = 'Неизвестное направление';
                if (b.destination_id) {
                    try {
                        const destResp = await fetch(`/destinations/${b.destination_id}`);
                        const dest = await destResp.json();
                        destName = dest.name || destName;
                    } catch (e) {
                        console.error('Ошибка получения направления:', e);
                    }
                }

                const col = document.createElement('div');
                col.className = 'col-md-6 mb-4';
                col.innerHTML = `
                    <div class="card bg-dark-gradient border-0 shadow-lg">
                      <div class="card-body">
                        <h5 class="card-title text-light">${destName}</h5>
                        <p class="card-text text-light mb-1"><strong>Забронировано мест:</strong> ${b.slots_reserved}</p>
                        <p class="card-text text-light mb-3"><strong>Дата бронирования:</strong> ${new Date(b.created_at).toLocaleString()}</p>
                        <button data-id="${b.id}" class="btn btn-secondary btn-delete-booking">
                          <i class="bi bi-trash-fill"></i> Отменить
                        </button>
                      </div>
                    </div>
                `;
                container.appendChild(col);
            })
        );

        // Навешиваем обработчики на кнопки удаления
        document.querySelectorAll('.btn-delete-booking').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = btn.dataset.id;
                if (!confirm('Вы уверены, что хотите отменить бронирование?')) return;
                try {
                    const res = await fetch(`/bookings/${id}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });
                    if (res.ok) {
                        fetchBookings();
                    } else {
                        throw new Error('Не удалось отменить');
                    }
                } catch (err) {
                    console.error(err);
                    alert('Ошибка: ' + err.message);
                }
            });
        });

    } catch (err) {
        console.error('FetchBookings Error:', err);
        noMsg.classList.remove('d-none');
    }
}