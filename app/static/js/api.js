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
  async getAll(status = "") {
    // если статус === "" — просто /trips
    const url = status
      ? `/trips?status=${encodeURIComponent(status)}`
      : `/trips`;
    return fetchAPI(url);
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

// --- Attractions API ---
const attractionsAPI = {
    async list(destId) {
      return fetchAPI(`/destinations/${destId}/attractions`);
    },
    async get(id) {
      return fetchAPI(`/attractions/${id}`);
    },
    async create(destId, data) {
      return fetchAPI(`/destinations/${destId}/attractions`, {
        method: 'POST',
        body: JSON.stringify(data)
      });
    },
    async update(id, data) {
      return fetchAPI(`/attractions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      });
    },
    async delete(id) {
      return fetchAPI(`/attractions/${id}`, {
        method: 'DELETE'
      });
    }
  };
  
  // --- Routes API ---
  const routesAPI = {
    async listByTrip(tripId) {
      return fetchAPI(`/trips/${tripId}/routes`);
    },
    async listMine() {
      return fetchAPI('/routes/mine');
    },
    async get(id) {
      return fetchAPI(`/routes/${id}`);
    },
    async create(tripId, data) {
      return fetchAPI(`/trips/${tripId}/routes`, {
        method: 'POST',
        body: JSON.stringify(data)
      });
    },
    async update(id, data) {
      return fetchAPI(`/routes/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      });
    },
    async delete(id) {
      return fetchAPI(`/routes/${id}`, {
        method: 'DELETE'
      });
    },
    async addAttraction(routeId, payload) {
      return fetchAPI(`/routes/${routeId}/attractions`, {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    },
    async moveAttraction(routeId, assocId, payload) {
      return fetchAPI(`/routes/${routeId}/attractions/${assocId}`, {
        method: 'PUT',
        body: JSON.stringify(payload)
      });
    },
    async removeAttraction(routeId, assocId) {
      return fetchAPI(`/routes/${routeId}/attractions/${assocId}`, {
        method: 'DELETE'
      });
    },
    async publish(routeId) {
      return fetchAPI(`/routes/${routeId}/publish`, {
        method: 'POST'
      });
    },
    async unpublish(routeId) {
      return fetchAPI(`/routes/${routeId}/publish`, { method: 'PUT' });
    }
  };
  
  // --- Public Routes API ---
  const publicRoutesAPI = {
    async list(filters = {}) {
      const params = new URLSearchParams({ published: true, ...filters });
      return fetchAPI(`/routes?${params.toString()}`);
    },
    async search(q) {
      return fetchAPI(`/routes/search?q=${encodeURIComponent(q)}`);
    }
  };

  const bookingsAPI = {
  async create(destinationId, slots) {
    const body = new URLSearchParams();
    body.append('destination_id', destinationId);
    body.append('slots_reserved', slots);

    const response = await fetch('/bookings/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body.toString()
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Ошибка бронирования' }));
      throw new Error(error.detail);
    }
    return response;
  },

  async listMine() {
    return fetchAPI('/bookings/me');
  },

  async delete(id) {
    return fetchAPI(`/bookings/${id}`, {
      method: 'DELETE'
    });
  }
};
