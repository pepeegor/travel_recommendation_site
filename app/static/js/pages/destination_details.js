document.addEventListener('DOMContentLoaded', async () => {
  const destinationId = window.location.pathname.split('/').pop();
  let latitude, longitude; // Declare latitude and longitude here

  try {
      const destination = await app.fetchApi(`/destinations/${destinationId}`);
      const reviews = await app.fetchApi(`/reviews/destination/${destinationId}`);
      renderDestinationDetails(destination, reviews.average_rating);
      renderReviews(reviews.reviews);

      // Assign values to latitude and longitude
      latitude = destination.latitude;
      longitude = destination.longitude;

      loadMapResources(latitude, longitude); 
  } catch (error) {
      console.error('Failed to fetch data:', error);
      app.showNotification('Ошибка при загрузке информации о направлении', 'danger');
  }
});

function renderDestinationDetails(destination, averageRating) {
  document.querySelector('.destination-name').textContent = destination.name;
  document.querySelector('.destination-rating').innerHTML = 
      averageRating 
          ? `<i class="bi bi-star-fill text-warning"></i> ${Number(averageRating).toFixed(1)} / 5` 
          : '<span class="text-muted">Нет оценок</span>'; 
  document.querySelector('.destination-description').textContent = destination.description;

  // Add code here to set other destination details like climate, price, images for the carousel
  // Example:
  // document.querySelector('.destination-climate').textContent = destination.climate;
  // document.querySelector('.destination-price').textContent = destination.approximate_price;
  // ... and so on
}

function renderReviews(reviews) {
  const reviewsContainer = document.getElementById('destination-reviews');
  reviewsContainer.innerHTML = ''; // Clear previous reviews

  if (reviews.length === 0) {
      reviewsContainer.innerHTML = '<p class="text-muted">Отзывов пока нет.</p>';
      return;
  }

  
  reviews.forEach(review => {
    const reviewElement = document.createElement('div');
    reviewElement.classList.add('review');
    reviewElement.innerHTML = `
        <p class="review-rating">
            <i class="bi bi-star-fill text-warning"></i> ${review.rating} / 5
        </p>
        <p class="review-text">${review.comment || ''}</p> 
        <p class="review-author text-muted"> - ${review.username}</p> 
    `;
    reviewsContainer.appendChild(reviewElement);
});
}

function initMap(latitude, longitude) {
  // Create a map using Leaflet
  const map = L.map('destination-map').setView([latitude, longitude], 12); // Adjust zoom level as needed

  // Add a tile layer (you can choose different tile providers)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  // Add a marker to the map
  L.marker([latitude, longitude]).addTo(map)
      .bindPopup(document.querySelector('.destination-name').textContent) // Use destination name as marker popup
      .openPopup();
}

// Load Leaflet CSS and JavaScript asynchronously
function loadMapResources(latitude, longitude) { // Accept latitude and longitude as arguments
  const leafletCss = document.createElement('link');
  leafletCss.rel = 'stylesheet';
  leafletCss.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
  document.head.appendChild(leafletCss);

  const leafletJs = document.createElement('script');
  leafletJs.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
  leafletJs.onload = function() {
      initMap(latitude, longitude); // Call initMap after Leaflet is loaded
  };
  document.body.appendChild(leafletJs);
}