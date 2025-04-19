function getCSRFToken() {
  let csrfToken = null;
  const cookies = document.cookie.split("; ");
  for (let cookie of cookies) {
      if (cookie.startsWith("csrftoken=")) {
          csrfToken = cookie.split("=")[1];
          break;
      }
  }
  return csrfToken;
}

let locationSent = false;

function fetchAndSendLocation() {
  if (navigator.geolocation && !locationSent) {
      navigator.geolocation.getCurrentPosition(
          (position) => {
              const data = {
                  latitude: position.coords.latitude,
                  longitude: position.coords.longitude,
              };

              fetch('/save-employee-location/', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                      'X-CSRFToken': getCSRFToken(),
                  },
                  body: JSON.stringify(data),
              })
              .then(response => response.json())
              .then(data => console.log("Location saved:", data))
              .catch(error => console.error("Error saving location"));

              locationSent = true;
          },
          (error) => console.error("Error getting location:", error),
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
  }
}

document.addEventListener("DOMContentLoaded", fetchAndSendLocation);
