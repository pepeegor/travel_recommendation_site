class HomePage {
    constructor() {
        this.init();
    }

    async init() {
        await this.loadPopularDestinations();
    }

    async loadPopularDestinations() {
        try {
            const destinations = await destinationsAPI.getPopular();

            // Получаем средние оценки для каждого направления
            const destinationsWithRatings = await Promise.all(
                destinations.map(async (dest) => {
                    const reviews = await app.fetchApi(`/reviews/destination/${dest.id}`);
                    return { ...dest, rating: reviews.average_rating };
                })
            );

            this.renderDestinations(destinationsWithRatings); // Передаем направления с рейтингами
        } catch (error) {
            console.error('Error loading destinations:', error);
            utils.showError('Ошибка при загрузке популярных направлений');
        }
    }

    renderDestinations(destinations) {
        const container = document.getElementById('popularDestinations');
        
        if (!destinations || !destinations.length) {
            container.innerHTML = `
                <div class="col-12 text-center">
                    <p class="text-muted">Направления не найдены</p>
                </div>
            `;
            return;
        }

        container.innerHTML = destinations.map(dest => this.renderDestinationCard(dest)).join('');
    }

    renderDestinationCard(destination) {
        const rating = destination.rating ? Number(destination.rating).toFixed(1) : 'Нет оценок';
        
        return `
            <div class="col-md-6 col-lg-4">
                <div class="card destination-card h-100">
                    <div class="card-img-overlay-wrap">
                        <img src="${destination.image_url}" 
                             class="card-img-top destination-image" 
                             alt="${this.escapeHtml(destination.name)}"
                             onerror="this.onerror=null; this.src='/static/images/placeholder-destination.jpg'">
                        <div class="card-img-overlay gradient-overlay">
                            <div class="destination-rating">
                                <i class="bi bi-star-fill"></i>
                                <span>${rating}</span>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">${this.escapeHtml(destination.name)}</h5>
                        <p class="card-text">
                            <i class="bi bi-geo-alt-fill"></i>
                            <span class="destination-location">${this.escapeHtml(destination.country)}</span>
                        </p>
                        <p class="card-text destination-description">
                            ${this.escapeHtml(destination.description || 'Описание отсутствует')}
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

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new HomePage();
});