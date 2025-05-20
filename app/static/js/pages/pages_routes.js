
document.addEventListener('DOMContentLoaded', () => {
  initMyRoutesPage();
});

async function initMyRoutesPage() {
  const listEl = document.getElementById('my-routes-list');
  if (!listEl) return;

  // Кнопка создания
  document.getElementById('create-route').addEventListener('click', () => {
    window.location.href = '/pages/routes/create';
  });

  try {
    // Получаем все свои маршруты
    const routes = await routesAPI.listMine();

    // Очищаем контейнер
    listEl.innerHTML = '';

    if (routes.length === 0) {
      listEl.innerHTML = '<div class="text-muted">У вас ещё нет сохранённых маршрутов.</div>';
      return;
    }

    // Рендерим каждый маршрут как ссылку
    routes.forEach(route => {
      const a = document.createElement('a');
      a.href = `/pages/routes/${route.id}`;  // ссылка на страницу деталей
      a.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
      a.innerHTML = `
        <span>${route.name}</span>
        <i class="bi bi-chevron-right"></i>
      `;
      listEl.append(a);
    });
  } catch (err) {
    console.error(err);
    showNotification(err.message || 'Ошибка при загрузке маршрутов', 'danger');
  }
}