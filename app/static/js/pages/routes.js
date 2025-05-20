document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('filter-form');
  form.addEventListener('submit', onFilter);
  // сразу загрузим список
  form.dispatchEvent(new Event('submit'));
});

async function onFilter(e) {
  e.preventDefault();
  const data = new FormData(e.target);
  const params = {};
  for (let [k, v] of data.entries()) {
    if (v !== "") params[k] = v;
  }

  try {
    const routes = await publicRoutesAPI.list(params);
    renderList(routes);
  } catch (err) {
    console.error(err);
    showNotification('Ошибка при загрузке маршрутов', 'danger');
  }
}

function renderList(routes) {
  const container = document.getElementById('routes-list');
  container.innerHTML = '';

  if (!routes.length) {
    container.innerHTML = '<p class="text-muted">Ничего не найдено.</p>';
    return;
  }

  routes.forEach(route => {
    const col = document.createElement('div');
    col.className = 'col-md-4 mb-4';
    col.innerHTML = `
      <div class="card h-100">
        <div id="mini-map-${route.id}" class="mini-map" style="height:200px;"></div>
        <div class="card-body d-flex flex-column">
          <h5 class="card-title">${route.name}</h5>
          <p class="card-text mb-2">Бюджет: ${route.total_budget ?? '—'} Br</p>
          <a href="/pages/routes/${route.id}" class="btn btn-sm btn-outline-primary mt-auto">
            Подробнее
          </a>
        </div>
      </div>
    `;
    container.appendChild(col);

    // В маршруте может быть поле `points` или `attractions`
    const pts = Array.isArray(route.points)
      ? route.points
      : Array.isArray(route.attractions)
        ? route.attractions
        : [];

    initMiniMap(`mini-map-${route.id}`, pts);
  });
}

function initMiniMap(elementId, pts) {
  // Если нет массива или он пуст
  if (!Array.isArray(pts) || !pts.length) {
    document.getElementById(elementId).innerHTML =
      '<p class="text-muted p-2">Нет точек для отображения</p>';
    return;
  }

  // Извлекаем объекты с координатами
  const coords = pts
    .map(pt => pt.attraction ?? pt)
    .filter(a => a && typeof a.latitude === 'number' && typeof a.longitude === 'number')
    .map(a => [a.latitude, a.longitude]);

  if (!coords.length) {
    document.getElementById(elementId).innerHTML =
      '<p class="text-muted p-2">Нет корректных координат</p>';
    return;
  }

  // создаём карту
  const map = L.map(elementId, {
    zoomControl: false,
    attributionControl: false
  }).setView(coords[0], coords.length > 1 ? 12 : 14);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

  if (coords.length > 1) {
    L.polyline(coords, { weight: 3 }).addTo(map);
    map.fitBounds(coords, { padding: [20, 20] });
  } else {
    L.marker(coords[0]).addTo(map);
  }
}
