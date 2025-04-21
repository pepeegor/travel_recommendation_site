// create_trip.js

document.addEventListener('DOMContentLoaded', function() {
  const createTripForm = document.getElementById('createTripForm');

  if (createTripForm) {
      createTripForm.addEventListener('submit', async function(event) {
          event.preventDefault();

          const destinationId = document.getElementById('destination').value;
          const startDate = document.getElementById('startDate').value;
          const endDate = document.getElementById('endDate').value;
          const budget = document.getElementById('budget').value; 
          const status = "planned";

          const tripData = {
              destination_id: parseInt(destinationId), 
              start_date: startDate, // No need to modify startDate here
              end_date: endDate,   // No need to modify endDate here
              budget: budget ? parseFloat(budget) : null,
              status: status
          };

          try {
              await tripsAPI.create(tripData);
              app.showNotification('Путешествие успешно создано!', 'success');
              window.location.href = '/pages/trips'; 
          } catch (error) {
              console.error('Ошибка при создании путешествия:', error);
              app.showNotification('Ошибка при создании путешествия', 'danger');
          }
      });
  }
});