async function fetchAPI(url, options = {}) {
    const defaultOptions = {
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/auth/login';
                return;
            }
            
            const error = await response.json();
            throw new Error(error.detail || 'Произошла ошибка');
        }

        return response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth API
const authAPI = {
    async login(credentials) {
        return fetchAPI('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    },

    async register(userData) {
        return fetchAPI('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },

    async logout() {
        return fetchAPI('/auth/logout', {
            method: 'POST'
        });
    },

    async getCurrentUser() {
        return fetchAPI('/auth/me');
    }
};

// Destinations API
const destinationsAPI = {
    async getPopular() {
        try {
            const response = await fetch('/destinations/popular');
            if (!response.ok) {
                throw new Error('Ошибка при загрузке популярных направлений');
            }
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch popular destinations:', error);
            throw error;
        }
    },

    async search(query) {
        return fetchAPI(`/destinations/search?query=${encodeURIComponent(query)}`);
    },

    async getById(id) {
        return fetchAPI(`/destinations/${id}`);
    },
};

// Trips API
const tripsAPI = {
    async getAll(status = '') {
        return fetchAPI(`/trips?status=${status}`);
    },

    async create(tripData) {
        return fetchAPI('/trips', {
            method: 'POST',
            body: JSON.stringify(tripData)
        });
    },

    async update(id, tripData) {
        return fetchAPI(`/trips/${id}`, { 
            method: 'PUT',
            body: JSON.stringify(tripData) 
        });
    },

    async delete(id) {
        return fetchAPI(`/trips/${id}`, {  // Исправлено: добавлен id в URL
            method: 'DELETE'
        });
    }
};

const reviewsAPI = {
    async getById(id) {
        return fetchAPI(`/reviews/${id}`);
    },

    async update(id, reviewData) {
        return fetchAPI(`/reviews/${id}`, {
            method: 'PUT',
            body: JSON.stringify(reviewData)
        });
    },

    async delete(id) {
        return fetchAPI(`/reviews/${id}`, {
            method: 'DELETE'
        });
    }
};