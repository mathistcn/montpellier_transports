// Initialiser la carte
let map = L.map('map').setView([43.611, 3.877], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Ajouter les arrêts
let stopMarkers = {};
stops.forEach(stop => {
    let marker = L.circleMarker([stop.stop_lat, stop.stop_lon], {radius: 5, color: 'blue'})
        .bindPopup(`<b>${stop.stop_name}</b>`)
        .addTo(map)
        .on('click', () => showStopSchedule(stop.stop_id, stop.stop_name));
    stopMarkers[stop.stop_id] = marker;
});

// Rafraîchir les positions des véhicules toutes les 15 secondes
async function updateVehicles() {
    const res = await fetch('/api/vehicle_positions');
    const vehicles = await res.json();

    if(window.vehicleLayer) window.vehicleLayer.clearLayers();
    window.vehicleLayer = L.layerGroup().addTo(map);

    vehicles.forEach(v => {
        L.marker([v.lat, v.lon], {rotationAngle: v.bearing})
            .bindPopup(`Trip: ${v.trip_id}, Route: ${v.route_id}`)
            .addTo(window.vehicleLayer);
    });
}

setInterval(updateVehicles, 15000);
updateVehicles();

// Afficher le planning pour un arrêt
async function showStopSchedule(stop_id, stop_name) {
    const res = await fetch(`/api/trip_updates/${stop_id}`);
    const trips = await res.json();

    const scheduleEl = document.getElementById('stop-schedule');
    scheduleEl.innerHTML = `<li><b>${stop_name}</b></li>`;
    if(trips.length === 0){
        scheduleEl.innerHTML += `<li>Aucun passage prévu pour l'instant</li>`;
        return;
    }

    trips.sort((a,b) => (a.arrival_time || 0) - (b.arrival_time || 0));

    trips.forEach(t => {
        let time = t.arrival_time ? new Date(t.arrival_time * 1000).toLocaleTimeString() : 'N/A';
        scheduleEl.innerHTML += `<li>Route ${t.route_name} : ${time}</li>`;
    });
}