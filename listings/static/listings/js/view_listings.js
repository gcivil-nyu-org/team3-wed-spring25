console.log("view_listings.js loaded");

document.addEventListener("DOMContentLoaded", function () {
  // View toggle functionality
  const listViewBtn = document.getElementById("list-view-btn");
  const mapViewBtn = document.getElementById("map-view-btn");
  const listView = document.getElementById("list-view");
  const mapView = document.getElementById("map-view");
  let map;

  function parseLocation(locationString) {
    try {
      const match = locationString.match(/\[([-\d.]+),\s*([-\d.]+)\]/);
      if (match) {
        return {
          lat: parseFloat(match[1]),
          lng: parseFloat(match[2]),
          address: locationString.split("[")[0].trim(),
          location_name: locationString.split("[")[0].trim(),
        };
      }
    } catch (error) {
      console.log("Error parsing location:", error);
    }
    return {
      lat: 40.69441, // Default to NYU tandon
      lng: -73.98653,
      address: locationString || "Location not specified",
    };
  }

  function initMap() {
    if (!map) {
      map = L.map("map-view").setView([43.6532, -79.3832], 13);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "© OpenStreetMap contributors",
      }).addTo(map);

      // Add markers for all listings
      const listings = document.querySelectorAll(".card");
      const bounds = [];

      listings.forEach((listing) => {
        const location = parseLocation(listing.dataset.location);
        const marker = L.marker([location.lat, location.lng]).addTo(map);
        bounds.push([location.lat, location.lng]);
        console.log(location);

        // Create popup content
        const title = listing.querySelector(".card-title").textContent;
        const price = listing.querySelector(
          ".card-text:nth-child(2)"
        ).textContent;

        const popupContent = `
          <strong>${title}</strong><br>
          ${location.location_name}<br>
          ${price}<br>
        `;
        marker.bindPopup(popupContent);
      });

      // Fit map to show all markers if there are any
      if (bounds.length > 0) {
        map.fitBounds(bounds);
      }
    }
  }

  function showListView() {
    mapView.classList.remove("active-view");
    listView.classList.add("active-view");
    listViewBtn.classList.add("btn-primary");
    listViewBtn.classList.remove("btn-outline-primary");
    mapViewBtn.classList.add("btn-outline-primary");
    mapViewBtn.classList.remove("btn-primary");
  }

  function showMapView() {
    listView.classList.remove("active-view");
    mapView.classList.add("active-view");
    mapViewBtn.classList.add("btn-primary");
    mapViewBtn.classList.remove("btn-outline-primary");

    // change list view button style since we are switching to map viewfd
    listViewBtn.classList.remove("btn-primary");
    listViewBtn.classList.add("btn-outline-primary");
    // remove active from list view button
    listViewBtn.classList.remove("active");

    initMap();
    if (map) {
      map.invalidateSize(); // Ensures map renders correctly
    }
  }

  // Event Listeners
  listViewBtn.addEventListener("click", showListView);
  mapViewBtn.addEventListener("click", showMapView);

  // Initialize with list view
  showListView();
});