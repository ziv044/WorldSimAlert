// Map Selector - Enable click-to-select locations on the map
const MapSelector = {
    active: false,
    map: null,
    callback: null,
    tempMarker: null,
    overlay: null,
    selectedLocation: null,

    init(mapInstance) {
        this.map = mapInstance;

        // Create overlay element
        this.overlay = document.createElement('div');
        this.overlay.className = 'map-selection-overlay';
        this.overlay.style.display = 'none';
        this.overlay.innerHTML = `
            <span class="map-selection-text">Click on the map to select location</span>
            <button class="btn btn-secondary btn-sm" id="map-select-cancel">Cancel</button>
            <button class="btn btn-primary btn-sm" id="map-select-confirm" disabled>Confirm</button>
        `;

        const mapContainer = document.querySelector('.map-container');
        if (mapContainer) {
            mapContainer.appendChild(this.overlay);
        }

        // Wire up overlay buttons
        this.overlay.querySelector('#map-select-cancel').addEventListener('click', () => this.cancel());
        this.overlay.querySelector('#map-select-confirm').addEventListener('click', () => this.confirm());
    },

    start(promptText, callback) {
        if (!this.map || !this.map.leafletMap) {
            console.error('Map not initialized');
            return;
        }

        this.active = true;
        this.callback = callback;
        this.selectedLocation = null;

        // Update overlay text
        this.overlay.querySelector('.map-selection-text').textContent = promptText || 'Click on the map to select location';
        this.overlay.querySelector('#map-select-confirm').disabled = true;
        this.overlay.style.display = 'flex';

        // Change cursor
        const mapEl = document.getElementById('map');
        if (mapEl) {
            mapEl.classList.add('map-selecting');
        }

        // Add click handler to map
        this.map.leafletMap.on('click', this.onMapClick.bind(this));

        // Close any open modal to show map
        if (Modal.activeModal) {
            Modal.close();
        }
    },

    onMapClick(e) {
        if (!this.active) return;

        const { lat, lng } = e.latlng;
        this.selectedLocation = { lat, lng };

        // Remove existing temp marker
        if (this.tempMarker) {
            this.map.leafletMap.removeLayer(this.tempMarker);
        }

        // Create new temp marker
        this.tempMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'map-marker map-marker-selected',
                html: '<div class="marker-icon marker-target">🎯</div>',
                iconSize: [32, 32],
                iconAnchor: [16, 16]
            })
        }).addTo(this.map.leafletMap);

        // Show coordinates in popup
        this.tempMarker.bindPopup(`
            <div class="selection-popup">
                <strong>Selected Location</strong><br>
                Lat: ${lat.toFixed(4)}<br>
                Lng: ${lng.toFixed(4)}
            </div>
        `).openPopup();

        // Enable confirm button
        this.overlay.querySelector('#map-select-confirm').disabled = false;
    },

    cancel() {
        this.cleanup();

        if (this.callback) {
            this.callback(null);
            this.callback = null;
        }
    },

    confirm() {
        if (!this.selectedLocation) return;

        const location = { ...this.selectedLocation };
        const callback = this.callback;

        this.cleanup();

        if (callback) {
            // Try to get location name via reverse geocoding (optional)
            this.getLocationName(location.lat, location.lng).then(name => {
                callback({
                    lat: location.lat,
                    lng: location.lng,
                    name: name || `${location.lat.toFixed(4)}, ${location.lng.toFixed(4)}`
                });
            });
        }
    },

    cleanup() {
        this.active = false;

        // Remove temp marker
        if (this.tempMarker && this.map && this.map.leafletMap) {
            this.map.leafletMap.removeLayer(this.tempMarker);
            this.tempMarker = null;
        }

        // Hide overlay
        if (this.overlay) {
            this.overlay.style.display = 'none';
        }

        // Reset cursor
        const mapEl = document.getElementById('map');
        if (mapEl) {
            mapEl.classList.remove('map-selecting');
        }

        // Remove click handler
        if (this.map && this.map.leafletMap) {
            this.map.leafletMap.off('click', this.onMapClick.bind(this));
        }

        this.selectedLocation = null;
    },

    async getLocationName(lat, lng) {
        // Simple reverse geocoding using Nominatim (free)
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`,
                { headers: { 'Accept-Language': 'en' } }
            );

            if (response.ok) {
                const data = await response.json();
                return data.display_name?.split(',')[0] || null;
            }
        } catch (error) {
            console.warn('Reverse geocoding failed:', error);
        }

        return null;
    },

    isActive() {
        return this.active;
    }
};
