// Events Panel Component
const EventsPanel = {
    container: null,
    events: [],
    countryCode: null,

    init(containerId) {
        this.container = document.getElementById(containerId);
    },

    async load(countryCode) {
        this.countryCode = countryCode;
        try {
            const data = await api.getEvents(countryCode);
            this.events = data.active_events || [];
            this.render();
        } catch (error) {
            console.error('Failed to load events:', error);
            this.container.innerHTML = '<div class="error">Failed to load events</div>';
        }
    },

    render() {
        if (!this.container) return;

        if (this.events.length === 0) {
            this.container.innerHTML = '<div class="empty-state">No active events</div>';
            return;
        }

        this.container.innerHTML = this.events.map(event => {
            const severityClass = this.getSeverityClass(event.severity);
            const eventName = this.formatEventName(event.event_id);

            return `
                <div class="event-item ${severityClass}" data-id="${event.event_id}">
                    <div class="event-name">${eventName}</div>
                    <span class="event-severity">${event.severity || 'unknown'}</span>
                    <div class="event-time">Started: ${event.started_date || 'Unknown'}</div>
                </div>
            `;
        }).join('');

        // Add click handlers for event response
        this.container.querySelectorAll('.event-item').forEach(item => {
            item.addEventListener('click', () => {
                this.showEventDetails(item.dataset.id);
            });
        });
    },

    getSeverityClass(severity) {
        if (!severity) return 'mild';
        const s = severity.toLowerCase();
        if (s === 'critical' || s === 'severe') return 'severe';
        if (s === 'high') return 'warning';
        return 'mild';
    },

    formatEventName(eventId) {
        if (!eventId) return 'Unknown Event';
        return eventId
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    },

    showEventDetails(eventId) {
        const event = this.events.find(e => e.event_id === eventId);
        if (!event) return;

        // Use EventActions to show response modal
        EventActions.showEventResponse(eventId);
    },

    getEvent(eventId) {
        return this.events.find(e => e.event_id === eventId);
    },

    addEvent(eventData) {
        // Add new event from WebSocket
        this.events.unshift({
            event_id: eventData.event_id,
            severity: eventData.severity,
            started_date: new Date().toISOString().split('T')[0]
        });
        this.render();
        this.flashEvent(eventData.event_id);
    },

    flashEvent(eventId) {
        const el = this.container?.querySelector(`[data-id="${eventId}"]`);
        if (el) {
            el.classList.add('flash');
            setTimeout(() => el.classList.remove('flash'), 2000);
        }
    },

    removeEvent(eventId) {
        this.events = this.events.filter(e => e.event_id !== eventId);
        this.render();
    },

    getEventCount() {
        return this.events.length;
    }
};
