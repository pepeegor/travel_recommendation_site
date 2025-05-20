document.addEventListener('DOMContentLoaded', () => {
    const filterEl = document.getElementById('destFilter');
    const listEl   = document.getElementById('routesList');
  
    // При изменении селекта — фильтруем
    filterEl.addEventListener('change', applyFilter);
  
    // Показываем всё изначально
    applyFilter();
  
    function applyFilter() {
      const selected = filterEl.value;  // "" или "3", "5" и т.д.
      // Берём все ссылки, у которых есть data-dest-id
      const items = listEl.querySelectorAll('a[data-dest-id]');
      items.forEach(item => {
        const destId = item.getAttribute('data-dest-id');
        // если ничего не выбрано, показываем всё, иначе скрываем те, что не совпадают
        if (!selected || destId === selected) {
          item.style.display = '';
        } else {
          item.style.display = 'none';
        }
      });
    }
  });
  