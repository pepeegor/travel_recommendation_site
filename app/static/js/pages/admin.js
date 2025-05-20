document.addEventListener('DOMContentLoaded', function () {

    // --- Статистика ---

    // Пример получения данных и построения графика с помощью Chart.js
    app.fetchApi('/pages/statistics') // Используем app.fetchApi из main.js
        .then(statisticsData => {
            // 1. Распределение поездок по месяцам
            const tripsPerMonthCtx = document.getElementById('tripsPerMonthChart').getContext('2d');
            new Chart(tripsPerMonthCtx, {
                type: 'line',
                data: {
                    labels: Object.keys(statisticsData.trips_per_month),
                    datasets: [{
                        label: 'Количество поездок',
                        data: Object.values(statisticsData.trips_per_month),
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                }
            });

            // 2. Топ-5 популярных направлений
            const topDestinationsData = statisticsData.top_destinations.slice(0, 5);
            const topDestinationsCtx = document.getElementById('topDestinationsChart').getContext('2d');
            new Chart(topDestinationsCtx, {
                type: 'pie',
                data: {
                    labels: topDestinationsData.map(dest => dest.name),
                    datasets: [{
                        label: 'Количество поездок',
                        data: topDestinationsData.map(dest => dest.trip_count),
                        backgroundColor: [
                            'rgb(255, 99, 132)',
                            'rgb(54, 162, 235)',
                            'rgb(255, 205, 86)',
                            'rgb(75, 192, 192)',
                            'rgb(153, 102, 255)'
                        ]
                    }]
                }
            });

            // 3. Средний рейтинг направлений
            const avgRatingsCtx = document.getElementById('avgRatingsChart').getContext('2d');
            new Chart(avgRatingsCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(statisticsData.avg_ratings),
                    datasets: [{
                        label: 'Средний рейтинг',
                        data: Object.values(statisticsData.avg_ratings),
                        backgroundColor: 'rgba(255, 159, 64, 0.2)',
                        borderColor: 'rgba(255, 159, 64, 1)',
                        borderWidth: 1
                    }]
                }
            });

            // 4. Распределение рейтинга по всем отзывам
            const ratingDistributionCtx = document.getElementById('ratingDistributionChart').getContext('2d');
            new Chart(ratingDistributionCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(statisticsData.rating_distribution),
                    datasets: [{
                        label: 'Количество отзывов',
                        data: Object.values(statisticsData.rating_distribution),
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                }
            });

            // 5. Соотношение цены и рейтинга направлений
            const priceRatingRelationCtx = document.getElementById('priceRatingRelationChart').getContext('2d');
            new Chart(priceRatingRelationCtx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Соотношение цены и рейтинга',
                        data: statisticsData.price_rating_relation.map(item => ({ x: item.price, y: item.rating })),
                        backgroundColor: 'rgb(153, 102, 255)'
                    }]
                }
            });
        })
        .catch(error => {
            console.error("Ошибка при получении данных статистики:", error);
        });


    // --- Управление пользователями ---

    // --- Модальное окно для создания пользователя ---
    const createUserModal = document.getElementById('createUserModal');
    const createUserForm = document.getElementById('createUserForm');

    createUserForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const username = document.getElementById('createUsername').value;
        const email = document.getElementById('createEmail').value;
        const password = document.getElementById('createPassword').value;
        const role = document.getElementById('createRole').value; // Получаем выбранную роль

        try {
            const newUser = await app.fetchApi('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password, role }), // Передаем роль в запросе
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            // Добавляем нового пользователя в таблицу
            const usersTable = document.querySelector('#users table tbody');
            const newRow = usersTable.insertRow();
            newRow.innerHTML = `
                <th scope="row">${newUser.id}</th> 
                <td>${username}</td>
                <td>${email}</td>
                <td>${role}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-primary edit-user-btn" data-bs-toggle="modal" data-bs-target="#editUserModal" data-user-id="${newUser.id}">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-danger delete-user-btn" data-user-id="${newUser.id}">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `; 

            app.showNotification('Пользователь успешно создан', 'success');
            createUserForm.reset();
            const modal = bootstrap.Modal.getInstance(createUserModal);
            modal.hide(); 

        } catch (error) {
            // Обработка ошибок уже выполняется в app.fetchApi
        }
    });


    // Обработчик для кнопок "Редактировать пользователя"
    const editUserBtns = document.querySelectorAll('.edit-user-btn');
    const editUserModal = document.getElementById('editUserModal');
    const editUserForm = document.getElementById('editUserForm');

    editUserBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.userId;
            // Получаем данные пользователя с сервера
            app.fetchApi('/auth/users/' + userId) 
                .then(user => {
                    // Заполняем поля модального окна данными пользователя
                    document.getElementById('editUserId').value = user.id;
                    document.getElementById('editUsername').value = user.username;
                    document.getElementById('editEmail').value = user.email;
                    document.getElementById('editRole').value = user.role; 
                })
                .catch(error => {
                    console.error("Ошибка при получении данных пользователя:", error);
                });
        });
    });

    // Обработчик отправки формы редактирования пользователя
    editUserForm.addEventListener('submit', async function (event) {
        event.preventDefault(); 

        const userId = document.getElementById('editUserId').value;
        const username = document.getElementById('editUsername').value;
        const email = document.getElementById('editEmail').value;
        const role = document.getElementById('editRole').value;

        try {
            // Отправляем PUT запрос для обновления данных пользователя
            await app.fetchApi('/auth/users/' + userId, { 
                method: 'PUT',
                body: JSON.stringify({ username, email, role })
            });

            // Обновляем данные пользователя в таблице
            const userRow = document.querySelector(`tr[data-user-id="${userId}"]`);
            if (userRow) {
                userRow.cells[1].textContent = username;
                userRow.cells[2].textContent = email;
                userRow.cells[3].textContent = role;
            }

            app.showNotification('Пользователь успешно обновлен', 'success');
            // Закрываем модальное окно после успешного обновления
            const modal = bootstrap.Modal.getInstance(editUserModal); 
            modal.hide(); 

        } catch (error) {
            // Обработка ошибок уже выполняется в app.fetchApi
        }
    });

    // Обработчик для кнопок "Удалить пользователя"
    const deleteUserBtns = document.querySelectorAll('.delete-user-btn');

    deleteUserBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.userId;
            if (confirm('Вы уверены, что хотите удалить этого пользователя?')) {
                // Отправляем DELETE запрос для удаления пользователя
                app.fetchApi('/auth/users/' + userId, { 
                    method: 'DELETE'
                })
                .then(() => {
                    // Удаляем пользователя из таблицы
                    const userRow = document.querySelector(`tr[data-user-id="${userId}"]`);
                    if (userRow) {
                        userRow.remove();
                    }
                    app.showNotification('Пользователь успешно удален', 'success');
                })
                .catch(error => {
                    console.error("Ошибка при удалении пользователя:", error);
                });
            }
        });
    });


    // --- Управление направлениями ---

    // --- Модальное окно для создания направления ---
    const createDestinationModal = document.getElementById('createDestinationModal');
    const createDestinationForm = document.getElementById('createDestinationForm');

    createDestinationForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const formData = new FormData(createDestinationForm);
        const destinationData = {};
        formData.forEach((value, key) => {
            destinationData[key] = value;
        });
        console.log(destinationData); // выводим данные в консоль

        try {
            const newDestination = await app.fetchApi('/destinations', {
                method: 'POST',
                body: JSON.stringify(destinationData),
            });

            const destinationsTable = document.querySelector('#destinations table tbody'); 
            const newRow = destinationsTable.insertRow();

            newRow.innerHTML = `
                <th scope="row">${newDestination.id}</th>
                <td>${newDestination.name}</td>
                <td>${newDestination.country}</td>
                <td>${newDestination.description}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-primary edit-destination-btn" data-bs-toggle="modal" data-bs-target="#editDestinationModal" data-destination-id="${newDestination.id}">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-danger delete-destination-btn" data-destination-id="${newDestination.id}">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;

            app.showNotification('Направление успешно создано', 'success');
            createDestinationForm.reset(); // Очищаем форму 
            const modal = bootstrap.Modal.getInstance(createDestinationModal);
            modal.hide(); // Закрываем модальное окно

        } catch (error) {
            if (error.toString().includes('UniqueViolationError')) {
                app.showNotification('Направление с таким ID уже существует', 'danger');
            } else {
                // Обработка других ошибок
                console.error("Ошибка при создании направления:", error); 
                app.showNotification('Ошибка при создании направления', 'danger');
            }
        }
    });

    const editDestinationBtns = document.querySelectorAll('.edit-destination-btn');
    const editDestinationModal = document.getElementById('editDestinationModal');
    const editDestinationForm = document.getElementById('editDestinationForm');

    editDestinationBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const destinationId = this.dataset.destinationId;
            app.fetchApi('/destinations/' + destinationId)
                .then(destination => {
                    document.getElementById('editDestinationId').value = destination.id;
                    document.getElementById('editDestinationName').value = destination.name;
                    document.getElementById('editDestinationCountry').value = destination.country;
                    document.getElementById('editDestinationDescription').value = destination.description;
                })
                .catch(error => {
                    console.error("Ошибка при получении данных направления:", error);
                });
        });
    });

    editDestinationForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const destinationId = document.getElementById('editDestinationId').value;
        const name = document.getElementById('editDestinationName').value;
        const country = document.getElementById('editDestinationCountry').value;
        const description = document.getElementById('editDestinationDescription').value;

        try {
            await app.fetchApi('/destinations/' + destinationId, {
                method: 'PUT',
                body: JSON.stringify({ name, country, description })
            });

            // Обновляем данные направления в таблице
            const destinationRow = document.querySelector(`tr[data-destination-id="${destinationId}"]`);
            if (destinationRow) {
                destinationRow.cells[1].textContent = name; 
                destinationRow.cells[2].textContent = country; 
                destinationRow.cells[3].textContent = description; 
            }

            app.showNotification('Направление успешно обновлено', 'success');
            const modal = bootstrap.Modal.getInstance(editDestinationModal);
            modal.hide();

        } catch (error) {
            // Обработка ошибок уже выполняется в app.fetchApi
        }
    });

    // Обработчик для кнопок "Удалить направление"
    const deleteDestinationBtns = document.querySelectorAll('.delete-destination-btn');

    deleteDestinationBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const destinationId = this.dataset.destinationId;
            if (confirm('Вы уверены, что хотите удалить это направление?')) {
                app.fetchApi('/destinations/' + destinationId, {
                    method: 'DELETE'
                })
                .then(() => {
                    // Удаляем направление из таблицы
                    const destinationRow = document.querySelector(`tr[data-destination-id="${destinationId}"]`);
                    if (destinationRow) {
                        destinationRow.remove();
                    }
                    app.showNotification('Направление успешно удалено', 'success');
                })
                .catch(error => {
                    console.error("Ошибка при удалении направления:", error);
                });
            }
        });
    });
    
        
});