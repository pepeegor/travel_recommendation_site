// static/js/pages/routes_edit.js

// Зависимости: Leaflet, attractionsAPI, routesAPI, showNotification, SortableJS

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    bindUI();
    initSortable();
    preloadRoute();
  });
  
  let map, markers = [], polyline = null;
  let availableAttractions = [], selectedPoints = [];
  
  /** Инициализация карты */
  function initMap() {
    map = L.map('route-create-map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  }
  
  /** Drag-n-drop для списка */
  function initSortable() {
    Sortable.create(document.getElementById('selectedPoints'), {
      handle: '.drag-handle',
      animation: 150,
      onEnd: () => {
        const lis = document.querySelectorAll('#selectedPoints li');
        selectedPoints = Array.from(lis).map((li, i) => {
          const old = selectedPoints.find(pt => pt.position == li.dataset.index);
          return { ...old, position: i };
        });
        renderLine();
      }
    });
  }
  
  /** UI-кнопки */
  function bindUI() {
    document.getElementById('selectTrip').addEventListener('change', onTripChange);
    document.getElementById('addPointBtn').addEventListener('click', showSuggestions);
    document.getElementById('suggestions').addEventListener('click', pickSuggestion);
    document.getElementById('routeName').addEventListener('input', validateForm);
    document.getElementById('saveRouteBtn').addEventListener('click', saveRoute);
  }
  
  /** При выборе поездки — сбрасываем и загружаем availableAttractions */
  async function onTripChange(e) {
    clearAll();
    const tripId = +e.target.value;
    const destId = +e.target.selectedOptions[0].dataset.destId;
    if (!tripId || !destId) return;
    try {
      availableAttractions = await attractionsAPI.list(destId);
      document.getElementById('addPointBtn').disabled = false;
      showNotification('Достопримечательности загружены', 'info');
    } catch {
      showNotification('Ошибка загрузки достопримечательностей', 'danger');
    }
    validateForm();
  }
  
  /** Показать подсказки */
  function showSuggestions() {
    const ul = document.getElementById('suggestions');
    ul.innerHTML = availableAttractions.map(a =>
      `<li class="list-group-item" data-id="${a.id}">${a.name} (${a.type})</li>`
    ).join('');
  }
  
  /** Выбор подсказки */
  function pickSuggestion(e) {
    if (e.target.tagName !== 'LI') return;
    const id = +e.target.dataset.id;
    const att = availableAttractions.find(x => x.id === id);
    if (!att) return;
    addPoint(att);
    document.getElementById('suggestions').innerHTML = '';
    validateForm();
  }
  
  /** Добавить точку */
  function addPoint(a) {
    const pos = selectedPoints.length;
    selectedPoints.push({ attraction: a, position: pos });
    const li = document.createElement('li');
    li.className = 'list-group-item d-flex justify-content-between align-items-center';
    li.dataset.index = pos;
    li.innerHTML = `
      <span><span class="drag-handle">☰</span>${a.name}</span>
      <button class="btn btn-sm btn-outline-danger remove">×</button>
    `;
    li.querySelector('.remove').onclick = () => removePoint(pos);
    li.addEventListener('mouseenter', () => map.setView([a.latitude, a.longitude], 15));
    document.getElementById('selectedPoints').append(li);
  
    const marker = L.marker([a.latitude, a.longitude]).addTo(map);
    markers.push(marker);
  
    renderLine();
  }
  
  /** Удалить точку */
  function removePoint(pos) {
    selectedPoints = selectedPoints.filter(pt => pt.position !== pos);
    document.querySelectorAll('#selectedPoints li').forEach(li => {
      if (+li.dataset.index === pos) li.remove();
    });
    markers[pos].remove();
    markers.splice(pos, 1);
    // обновляем индексы
    selectedPoints = selectedPoints.map((pt, i) => ({ ...pt, position: i }));
    document.querySelectorAll('#selectedPoints li').forEach((li, i) => {
      li.dataset.index = i;
    });
    renderLine();
    validateForm();
  }
  
  /** Рисуем линию */
  function renderLine() {
    const pts = selectedPoints.map(pt => [pt.attraction.latitude, pt.attraction.longitude]);
    if (polyline) map.removeLayer(polyline);
    if (pts.length) {
      polyline = L.polyline(pts, { color: 'blue', weight: 4 }).addTo(map);
      map.fitBounds(polyline.getBounds());
    }
  }
  
  /** Валидация */
  function validateForm() {
    const ok = !!(
      document.getElementById('routeName').value.trim() &&
      document.getElementById('selectTrip').value &&
      selectedPoints.length
    );
    document.getElementById('saveRouteBtn').disabled = !ok;
  }
  
  /** Сброс всего */
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
  
  /** Предзагрузка существующих точек */
  async function preloadRoute() {
    const data = window.routeData;
    if (!data) return;
    document.getElementById('routeName').value = data.name;
    // выбираем поездку
    const sel = document.getElementById('selectTrip');
    sel.value = data.trip_id;
    await onTripChange({ target: sel });
  
    // добавляем точки
    if (Array.isArray(data.points)) {
      data.points
        .sort((a, b) => a.position - b.position)
        .forEach(pt => addPoint(pt.attraction));
    }
    validateForm();
  }
  
  /** Сохранение */
  async function saveRoute(e) {
    e.preventDefault();
  
    const tripEl = document.getElementById('selectTrip');
    const tripId = Number(tripEl.value);
    const name = document.getElementById('routeName').value.trim();
    const destId = Number(tripEl.selectedOptions[0].dataset.destId);
  
    // собираем массив точек
    const attractions = selectedPoints.map(pt => ({
      attraction_id: pt.attraction.id,
      position: pt.position
    }));
  
    try {
      // единый запрос на обновление всех полей + точек
      await routesAPI.update(window.routeData.id, {
        name,
        trip_id: tripId,
        destination_id: destId,
        attractions
      });
      showNotification('Маршрут обновлён', 'success');
      setTimeout(() => {
        window.location.href = `/pages/routes/${window.routeData.id}`;
      }, 800);
    } catch (err) {
      console.error(err);
      const msg = err.detail || err.message || 'Ошибка при сохранении';
      showNotification(msg, 'danger');
    }  
  }
  