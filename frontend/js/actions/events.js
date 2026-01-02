// Event Response Actions
const EventActions = {
    async showEventResponse(eventId) {
        const event = EventsPanel.getEvent ? EventsPanel.getEvent(eventId) : null;

        if (!event) {
            // Try to fetch from API
            try {
                const result = await api.getEvents(App.countryCode);
                const events = result.active_events || [];
                const found = events.find(e => e.event_id === eventId);
                if (found) {
                    this.showEventDetails(found);
                } else {
                    Modal.showResult('Error', 'Event not found', false);
                }
            } catch (error) {
                Modal.showResult('Error', 'Failed to load event: ' + error.message, false);
            }
            return;
        }

        this.showEventDetails(event);
    },

    showEventDetails(event) {
        const severityClass = this.getSeverityClass(event.severity);

        // Default responses if none provided
        const responses = event.responses || [
            { id: 'accept', label: 'Accept' },
            { id: 'reject', label: 'Reject' },
            { id: 'ignore', label: 'Ignore' }
        ];

        Modal.show({
            title: event.event_name || this.formatEventName(event.event_id),
            content: `
                <div class="event-details">
                    <div class="event-severity-badge ${severityClass}">
                        ${event.severity || 'Unknown'} Severity
                    </div>

                    ${event.description ? `
                        <p class="event-description">${event.description}</p>
                    ` : ''}

                    <div class="event-info">
                        <div class="event-info-row">
                            <span class="event-info-label">Started:</span>
                            <span class="event-info-value">${event.started_date || 'Unknown'}</span>
                        </div>
                        ${event.expires_date ? `
                            <div class="event-info-row">
                                <span class="event-info-label">Expires:</span>
                                <span class="event-info-value">${event.expires_date}</span>
                            </div>
                        ` : ''}
                    </div>

                    ${event.effects ? `
                        <div class="event-effects">
                            <h4>Effects:</h4>
                            ${this.renderEffects(event.effects)}
                        </div>
                    ` : ''}

                    <div class="event-responses">
                        <h4>Choose Response:</h4>
                        <div class="response-buttons">
                            ${responses.map(r => `
                                <button class="btn btn-secondary response-btn" data-response="${r.id}">
                                    ${r.label}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `,
            buttons: [
                { label: 'Close (No Action)', onClick: () => Modal.close() }
            ]
        });

        // Wire up response buttons
        document.querySelectorAll('.response-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const responseId = btn.dataset.response;
                await this.respond(event.event_id, responseId);
            });
        });
    },

    formatEventName(eventId) {
        if (!eventId) return 'Unknown Event';
        return eventId
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    },

    getSeverityClass(severity) {
        if (!severity) return 'severity-mild';
        const s = severity.toLowerCase();
        if (s === 'critical' || s === 'severe') return 'severity-critical';
        if (s === 'high') return 'severity-high';
        if (s === 'medium' || s === 'moderate') return 'severity-medium';
        return 'severity-mild';
    },

    renderEffects(effects) {
        if (!effects) return '<p>No specific effects listed.</p>';

        if (typeof effects === 'string') {
            return `<p>${effects}</p>`;
        }

        if (Array.isArray(effects)) {
            return `<ul>${effects.map(e => `<li>${e}</li>`).join('')}</ul>`;
        }

        if (typeof effects === 'object') {
            return `<ul>${Object.entries(effects).map(([key, val]) =>
                `<li><strong>${key}:</strong> ${val}</li>`
            ).join('')}</ul>`;
        }

        return '<p>Effects data unavailable.</p>';
    },

    async respond(eventId, responseId) {
        try {
            const result = await api.respondToEvent(App.countryCode, eventId, responseId);
            Modal.close();

            if (result.success !== false) {
                App.showNotification('Response submitted', 'success');
                EventsPanel.load && EventsPanel.load(App.countryCode);
                KPIPanel.load && KPIPanel.load(App.countryCode);
            } else {
                Modal.showResult('Response Failed', result.error || result.message || 'Failed to submit response', false);
            }
        } catch (error) {
            Modal.showResult('Error', error.message, false);
        }
    }
};
