document.addEventListener('DOMContentLoaded', () => {
  fetchDestinations();
  initializeFilters();
});

// Fetch destinations with applied filters
async function fetchDestinations(filters = {}) {
  try {
    // Form the URL with filter parameters
    let url = '/destinations?'; 
    for (const key in filters) {
      url += `${key}=${encodeURIComponent(filters[key])}&`;
    }
    if (url.endsWith('&')) {
      url = url.slice(0, -1);
    }

    const response = await fetch(url); 
    if (!response.ok) {
      const errorData = await response.text(); 
      throw new Error(`Ошибка сервера: ${response.status} - ${errorData}`);
    }
    const destinations = await response.json();

    // Get average ratings (replace with your actual implementation)
    const destinationsWithRatings = await Promise.all(
      destinations.map(async (dest) => {
        const reviews = await app.fetchApi(`/reviews/destination/${dest.id}`);
        return { ...dest, rating: reviews.average_rating };
      })
    );

    renderDestinations(destinationsWithRatings);
  } catch (error) {
    console.error('Failed to fetch destinations:', error);
    app.showNotification(error.message, 'danger');
  }
}

function renderDestinations(destinations) {
  const container = document.getElementById('destinations-list');
  container.innerHTML = ''; // Очищаем список перед обновлением

  if (!destinations || !destinations.length) {
    container.innerHTML = `
        <div class="col-12 text-center">
          <p class="text-muted">Направления не найдены</p>
        </div>
    `;
    return;
  }

  container.innerHTML = destinations.map(dest => renderDestinationCard(dest)).join('');
}

function renderDestinationCard(destination) {
  const rating = destination.rating ? Number(destination.rating).toFixed(1) : 'Нет оценок';
  const approximatePrice = destination.approximate_price
    ? `Примерная цена: ${destination.approximate_price}`
    : 'Цена поездки не указана';

  return `
    <div class="col-md-6 col-lg-4">
        <div class="card destination-card h-100">
            <div class="card-img-overlay-wrap">
                <img src="${destination.image_url}" 
                    class="card-img-top destination-image" 
                    alt="${escapeHtml(destination.name)}"
                    onerror="this.onerror=null; this.src='/static/images/placeholder-destination.jpg'">
                <div class="card-img-overlay gradient-overlay">
                    <div class="destination-rating">
                        <i class="bi bi-star-fill"></i>
                        <span>${rating}</span>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <h5 class="card-title">${escapeHtml(destination.name)}</h5>
                <p class="card-text">
                    <i class="bi bi-geo-alt-fill"></i>
                    <span class="destination-location">${escapeHtml(destination.country)}</span>
                </p>
                <p class="card-text destination-description">
                    ${escapeHtml(destination.description || 'Описание отсутствует')}
                </p>
                <p class="card-text destination-price">
                    ${approximatePrice}
                </p> 
            </div>
            <div class="card-footer bg-transparent border-top-0">
                <div class="d-flex justify-content-between align-items-center">
                    <a href="/pages/destinations/${destination.id}" 
                        class="btn btn-outline-primary btn-sm stretched-link">
                        Подробнее
                    </a>
                </div>
            </div>
        </div>
    </div>
  `;
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Initialize filters
async function initializeFilters() {
  const filtersContainer = document.getElementById('filters');

  try {
    const destinations = await app.fetchApi('/destinations');

    // Country filter
    const countries = [...new Set(destinations.map(dest => dest.country))].sort();
    const countryFilter = createFilterDropdown('Страна', countries, 'country');
    filtersContainer.appendChild(countryFilter);

    // Price filter
    const priceRanges = [
      { label: 'До 1000$', value: '1000' },
      { label: '1000$ - 3000$', value: '1000-3000' },
      { label: '3000$ - 5000$', value: '3000-5000' },
      { label: 'Более 5000$', value: '5000+' }
    ];
    const priceFilter = createFilterDropdown('Цена', priceRanges, 'price', true);
    filtersContainer.appendChild(priceFilter);
  } catch (error) {
    console.error('Failed to initialize filters:', error);
    app.showNotification('Ошибка при инициализации фильтров', 'danger');
  }
}

// Create a filter dropdown component
function createFilterDropdown(label, options, name, useLabels = false) {
  const filterDiv = document.createElement('div');
  filterDiv.className = 'mb-3';

  const labelElement = document.createElement('label');
  labelElement.className = 'form-label';
  labelElement.textContent = label;
  filterDiv.appendChild(labelElement);

  const selectElement = document.createElement('select');
  selectElement.className = 'form-select';
  selectElement.name = name;
  selectElement.innerHTML = '<option value="">Все</option>'; // Add an "All" option

  options.forEach(option => {
    if (useLabels) {
      selectElement.innerHTML += `<option value="${option.value}">${option.label}</option>`;
    } else {
      selectElement.innerHTML += `<option value="${option}">${option}</option>`;
    }
  });

  filterDiv.appendChild(selectElement);

  return filterDiv;
}

const searchForm = document.querySelector('form[action="/pages/destinations"]');
const filtersContainer = document.getElementById('filters');

searchForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const searchTerm = document.getElementById('search-input').value;
  console.log(searchTerm);
  const filters = { search: searchTerm }; // Start with search term

  // Get values from other filters
  const filterElements = filtersContainer.querySelectorAll('select');
  filterElements.forEach(filter => {
    const value = filter.value;
    if (value) {
      filters[filter.name] = value;
    }
  });

  fetchDestinations(filters); // Fetch with all filters
});

