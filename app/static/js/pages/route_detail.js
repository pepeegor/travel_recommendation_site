
document.addEventListener('DOMContentLoaded', () => {
    const data = window.routeData;
    const pts = data.points || [];
    if (!pts.length) return;
  
    // 1) Инициализируем карту на первой точке
    const first = pts[0].attraction;
    const map = L.map('route-map').setView(
      [first.latitude, first.longitude],
      13
    );
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
      .addTo(map);
  
    // 2) Рисуем полилинию
    const coords = pts
      .sort((a, b) => a.position - b.position)
      .map(p => [p.attraction.latitude, p.attraction.longitude]);
    const poly = L.polyline(coords, { color: '#c8a45d', weight: 4 })
      .addTo(map);
    map.fitBounds(poly.getBounds(), { padding: [20, 20] });
  
    // 3) Ставим маркеры
    const markers = pts.map(p =>
      L.marker([p.attraction.latitude, p.attraction.longitude])
        .addTo(map)
        .bindPopup(`<b>${p.attraction.name}</b>`)
    );
  
    // 4) Наведение на пункт списка — центрируем и открываем попап
    document.querySelectorAll('.point-item').forEach((el, idx) => {
      el.addEventListener('mouseenter', () => {
        const pt = pts[idx].attraction;
        map.setView([pt.latitude, pt.longitude], 15);
        markers[idx].openPopup();
      });
    });
  
    // 5) Кнопка «Опубликовать»
    const btnPub = document.getElementById('publishBtn');
    if (btnPub) {
      btnPub.addEventListener('click', async () => {
        btnPub.disabled = true;
        btnPub.innerHTML = '<i class="bi bi-arrow-repeat bi-spin"></i> Публикация...';
        try {
          await routesAPI.publish(data.id);
          showNotification('Маршрут опубликован', 'success');
          // Заменим кнопку на статус
          btnPub.outerHTML = '<span class="badge bg-success">Опубликован</span>';
        } catch (e) {
          console.error(e);
          btnPub.disabled = false;
          btnPub.innerHTML = '<i class="bi bi-upload"></i> Опубликовать';
          showNotification('Не удалось опубликовать', 'danger');
        }
      });
    }
  
    // 6) Кнопка «Снять публикацию»
    const btnUnpub = document.getElementById('unpublishBtn');
    if (btnUnpub) {
      btnUnpub.addEventListener('click', async () => {
        btnUnpub.disabled = true;
        btnUnpub.innerHTML = '<i class="bi bi-arrow-repeat bi-spin"></i> Снятие...';
        try {
          await routesAPI.unpublish(data.id);
          showNotification('Публикация снята', 'success');
          // Перезагрузим страницу, чтобы появились кнопки «Опубликовать» и «Редактировать»
          setTimeout(() => location.reload(), 500);
        } catch (e) {
          console.error(e);
          btnUnpub.disabled = false;
          btnUnpub.innerHTML = '<i class="bi bi-download"></i> Снять публикацию';
          showNotification('Не удалось снять публикацию', 'danger');
        }
      });
    }
  });