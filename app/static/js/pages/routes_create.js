// static/js/pages/routes_create.js

// Зависимости: Leaflet, attractionsAPI, routesAPI, showNotification, SortableJS

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    bindUI();
    initSortable();
    validateForm();
  });
  
  let map, markers = [], polyline = null;
  let availableAttractions = [], selectedPoints = [];
  
  /** Инициализация карты */
  function initMap() {
    map = L.map('route-create-map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  }
  
  /** Drag-and-drop для списка точек */
  function initSortable() {
    Sortable.create(document.getElementById('selectedPoints'), {
      handle: '.drag-handle',
      animation: 150,
      onEnd: () => {
        // перестроить порядок selectedPoints
        const lis = document.querySelectorAll('#selectedPoints li');
        selectedPoints = Array.from(lis).map((li, i) => {
          const old = selectedPoints.find(pt => pt.position == li.dataset.index);
          return { ...old, position: i };
        });
        renderLine();
      }
    });
  }
  
  /** Привязка UI-событий */
  function bindUI() {
    document.getElementById('selectTrip')
      .addEventListener('change', onTripChange);
    document.getElementById('addPointBtn')
      .addEventListener('click', showSuggestions);
    document.getElementById('suggestions')
      .addEventListener('click', pickSuggestion);
    document.getElementById('routeName')
      .addEventListener('input', validateForm);
    document.getElementById('saveRouteBtn')
      .addEventListener('click', saveRoute);
  }
  
  /** При выборе поездки подгружаем достопримечательности */
  async function onTripChange(e) {
    clearAll();
    const tripSelect = e.target;
    const tripId = +tripSelect.value;
    const destId = +tripSelect.selectedOptions[0].dataset.destId;
    if (!tripId || !destId) return;
    try {
      availableAttractions = await attractionsAPI.list(destId);
      document.getElementById('addPointBtn').disabled = false;
      showNotification('Достопримечательности загружены', 'info');
    } catch {
      showNotification('Ошибка загрузки мест', 'danger');
    }
    validateForm();
  }
  
  /** Показать все подтянутые места как подсказки */
  function showSuggestions() {
    const ul = document.getElementById('suggestions');
    ul.innerHTML = availableAttractions.map(a =>
      `<li class="list-group-item" data-id="${a.id}">
         ${a.name} (${a.type}) — примерная цена ${a.approximate_price}
       </li>`
    ).join('');
  }
  
  /** Клик по подсказке – добавляем точку */
  function pickSuggestion(e) {
    if (e.target.tagName !== 'LI') return;
    const id = +e.target.dataset.id;
    const a = availableAttractions.find(x => x.id === id);
    if (!a) return;
    addPoint(a);
    document.getElementById('suggestions').innerHTML = '';
    validateForm();
  }
  
  /** Добавление точки в маршрут */
  function addPoint(a) {
    const pos = selectedPoints.length;
    selectedPoints.push({ attraction: a, position: pos });
  
    const li = document.createElement('li');
    li.className = 'list-group-item d-flex justify-content-between align-items-center';
    li.dataset.index = pos;
    li.innerHTML = `
      <span><span class="drag-handle">☰</span>${a.name}</span>
      <button type="button" class="btn btn-sm btn-outline-danger remove">×</button>
    `;
    li.addEventListener('mouseenter', () => {
      map.setView([a.latitude, a.longitude], 15);
    });
    li.querySelector('.remove').onclick = () => removePoint(pos);
    document.getElementById('selectedPoints').append(li);
  
    const marker = L.marker([a.latitude, a.longitude]).addTo(map);
    markers.push(marker);
    renderLine();
  }
  
  /** Удалить точку */
  function removePoint(pos) {
    // из данных
    selectedPoints = selectedPoints.filter(pt => pt.position !== pos);
    // из DOM
    document.querySelectorAll('#selectedPoints li').forEach(li => {
      if (+li.dataset.index === pos) li.remove();
    });
    // маркер
    markers[pos].remove();
    markers.splice(pos, 1);
    // пересчет позиций
    selectedPoints = selectedPoints.map((pt, i) => ({ ...pt, position: i }));
    document.querySelectorAll('#selectedPoints li').forEach((li, i) => {
      li.dataset.index = i;
    });
    renderLine();
    validateForm();
  }
  
  /** Отрисовать полилинию */
  function renderLine() {
    const pts = selectedPoints.map(pt => [pt.attraction.latitude, pt.attraction.longitude]);
    if (polyline) map.removeLayer(polyline);
    polyline = L.polyline(pts, { color: 'blue', weight: 4 }).addTo(map);
    if (pts.length) map.fitBounds(polyline.getBounds());
  }
  
  /** Проверка возможности сохранить */
  function validateForm() {
    const ok = !!(
      document.getElementById('routeName').value.trim() &&
      document.getElementById('selectTrip').value &&
      selectedPoints.length
    );
    document.getElementById('saveRouteBtn').disabled = !ok;
  }
  
  /** Очистить всё */
  function clearAll() {
    selectedPoints = [];
    availableAttractions = [];
    document.getElementById('selectedPoints').innerHTML = '';
    document.getElementById('suggestions').innerHTML = '';
    document.getElementById('addPointBtn').disabled = true;
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    if (polyline) { map.removeLayer(polyline); polyline = null; }
  }
  
  /** Сохранение маршрута и точек */
  async function saveRoute(e) {
    e.preventDefault();
    const tripEl = document.getElementById('selectTrip');
    const tripId = Number(tripEl.value);
    const name = document.getElementById('routeName').value.trim();
    const destId = Number(tripEl.selectedOptions[0].dataset.destId);
  
    try {
      const route = await routesAPI.create(tripId, {
        name,
        destination_id: destId
      });
      for (let pt of selectedPoints) {
        await routesAPI.addAttraction(route.id, {
          attraction_id: pt.attraction.id,
          position: pt.position
        });
      }
      showNotification('Маршрут сохранён', 'success');
      setTimeout(() => {
        window.location.href = `/pages/routes/${route.id}`;
      }, 800);
    } catch (err) {
      console.error(err);
      const msg = err.detail || err.message || 'Ошибка при сохранении';
      showNotification(msg, 'danger');
    }
  }
  