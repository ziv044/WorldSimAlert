// Modal System - Reusable dialogs and forms for World Sim
const Modal = {
    container: null,
    activeModal: null,
    onCloseCallback: null,

    init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = containerId;
            document.body.appendChild(this.container);
        }

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.close();
            }
        });
    },

    show(config) {
        // config: { title, content, buttons[], onClose, size, className }
        const { title, content, buttons = [], onClose, size = 'medium', className = '' } = config;

        this.onCloseCallback = onClose;

        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop';
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) this.close();
        });

        const sizeClass = size === 'large' ? 'modal-large' : size === 'small' ? 'modal-small' : '';

        backdrop.innerHTML = `
            <div class="modal ${sizeClass} ${className}">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="modal-close" type="button">&times;</button>
                </div>
                <div class="modal-body">
                    ${typeof content === 'string' ? content : ''}
                </div>
                ${buttons.length > 0 ? `
                    <div class="modal-footer">
                        ${buttons.map(btn => `
                            <button class="btn ${btn.primary ? 'btn-primary' : btn.danger ? 'btn-danger' : 'btn-secondary'}"
                                    data-action="${btn.action || ''}"
                                    ${btn.disabled ? 'disabled' : ''}>
                                ${btn.label}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        // If content is a DOM element, append it
        if (typeof content !== 'string' && content instanceof HTMLElement) {
            backdrop.querySelector('.modal-body').appendChild(content);
        }

        this.container.appendChild(backdrop);
        this.activeModal = backdrop;

        // Wire up close button
        backdrop.querySelector('.modal-close').addEventListener('click', () => this.close());

        // Wire up footer buttons
        buttons.forEach((btn, index) => {
            const btnEl = backdrop.querySelectorAll('.modal-footer .btn')[index];
            if (btnEl && btn.onClick) {
                btnEl.addEventListener('click', () => btn.onClick());
            }
        });

        // Animate in
        requestAnimationFrame(() => {
            backdrop.classList.add('show');
        });

        return backdrop;
    },

    close() {
        if (!this.activeModal) return;

        // Capture reference to the modal being closed
        const modalToClose = this.activeModal;
        const callbackToRun = this.onCloseCallback;

        // Clear references immediately to allow new modals
        this.activeModal = null;
        this.onCloseCallback = null;

        modalToClose.classList.remove('show');

        setTimeout(() => {
            modalToClose.remove();
            if (callbackToRun) {
                callbackToRun();
            }
        }, 200);
    },

    showForm(config) {
        // config: { title, fields[], onSubmit, onCancel, submitLabel, cancelLabel }
        const {
            title,
            fields = [],
            onSubmit,
            onCancel,
            submitLabel = 'Submit',
            cancelLabel = 'Cancel',
            size = 'medium'
        } = config;

        const formId = 'modal-form-' + Date.now();
        const formContent = this.buildForm(fields, formId);

        const modal = this.show({
            title,
            content: formContent,
            size,
            buttons: [
                {
                    label: cancelLabel,
                    onClick: () => {
                        if (onCancel) onCancel();
                        this.close();
                    }
                },
                {
                    label: submitLabel,
                    primary: true,
                    onClick: async () => {
                        const form = document.getElementById(formId);
                        if (!form.checkValidity()) {
                            form.reportValidity();
                            return;
                        }

                        const data = this.getFormData(form, fields);
                        const submitBtn = modal.querySelector('.btn-primary');

                        // Show loading state
                        submitBtn.disabled = true;
                        submitBtn.innerHTML = '<span class="spinner"></span> Processing...';

                        try {
                            await onSubmit(data);
                            this.close();
                        } catch (error) {
                            console.error('Form submission error:', error);
                            submitBtn.disabled = false;
                            submitBtn.textContent = submitLabel;
                            this.showError(error.message || 'An error occurred');
                        }
                    }
                }
            ]
        });

        // Setup field change handlers
        fields.forEach(field => {
            if (field.onChange) {
                const el = document.querySelector(`[name="${field.name}"]`);
                if (el) {
                    el.addEventListener('change', (e) => field.onChange(e.target.value, modal));
                }
            }
        });

        // Setup range value displays
        modal.querySelectorAll('.form-range').forEach(range => {
            const display = range.parentElement.querySelector('.form-range-value');
            if (display) {
                range.addEventListener('input', () => {
                    const suffix = range.dataset.suffix || '';
                    display.textContent = range.value + suffix;
                });
            }
        });

        return modal;
    },

    buildForm(fields, formId) {
        return `
            <form id="${formId}" class="modal-form">
                ${fields.map(field => this.buildField(field)).join('')}
            </form>
        `;
    },

    buildField(field) {
        const {
            name, type, label, options, required = true,
            defaultValue, min, max, step, description,
            placeholder, rows, suffix
        } = field;

        let input = '';

        switch (type) {
            case 'text':
                input = `<input type="text" name="${name}" class="form-input"
                    ${required ? 'required' : ''}
                    ${placeholder ? `placeholder="${placeholder}"` : ''}
                    ${defaultValue ? `value="${defaultValue}"` : ''}>`;
                break;

            case 'number':
                input = `<input type="number" name="${name}" class="form-input"
                    ${required ? 'required' : ''}
                    ${min !== undefined ? `min="${min}"` : ''}
                    ${max !== undefined ? `max="${max}"` : ''}
                    ${step !== undefined ? `step="${step}"` : ''}
                    ${defaultValue !== undefined ? `value="${defaultValue}"` : ''}>`;
                break;

            case 'select':
                input = `<select name="${name}" class="form-select" ${required ? 'required' : ''}>
                    <option value="">-- Select --</option>
                    ${(options || []).map(opt => {
                        const val = typeof opt === 'object' ? opt.value : opt;
                        const lbl = typeof opt === 'object' ? opt.label : opt;
                        const selected = defaultValue === val ? 'selected' : '';
                        return `<option value="${val}" ${selected}>${lbl}</option>`;
                    }).join('')}
                </select>`;
                break;

            case 'range':
                const rangeMin = min || 0;
                const rangeMax = max || 100;
                const rangeStep = step || 1;
                const rangeDefault = defaultValue !== undefined ? defaultValue : rangeMin;
                const rangeSuffix = suffix || '';
                input = `<div class="form-range-container">
                    <input type="range" name="${name}" class="form-range"
                        min="${rangeMin}" max="${rangeMax}" step="${rangeStep}"
                        value="${rangeDefault}" data-suffix="${rangeSuffix}">
                    <span class="form-range-value">${rangeDefault}${rangeSuffix}</span>
                </div>`;
                break;

            case 'textarea':
                input = `<textarea name="${name}" class="form-textarea"
                    ${required ? 'required' : ''}
                    rows="${rows || 3}"
                    ${placeholder ? `placeholder="${placeholder}"` : ''}>${defaultValue || ''}</textarea>`;
                break;

            case 'checkbox':
                input = `<label class="form-checkbox">
                    <input type="checkbox" name="${name}" ${defaultValue ? 'checked' : ''}>
                    <span>${label}</span>
                </label>`;
                return `<div class="form-group form-group-checkbox">${input}</div>`;

            case 'display':
                input = `<div class="form-display" id="${name}">${defaultValue || ''}</div>`;
                break;

            case 'unit-select':
                input = `<div class="unit-select-list" id="${name}-list">
                    ${(options || []).map(unit => `
                        <div class="unit-select-item">
                            <label>
                                <input type="checkbox" name="${name}" value="${unit.id}"
                                    ${unit.disabled ? 'disabled' : ''}>
                                <span class="unit-select-name">${unit.name}</span>
                                <span class="unit-select-status ${unit.status}">${unit.status}</span>
                            </label>
                        </div>
                    `).join('')}
                </div>`;
                break;

            default:
                input = `<input type="text" name="${name}" class="form-input">`;
        }

        return `
            <div class="form-group">
                ${type !== 'checkbox' ? `<label class="form-label">${label}${required ? ' *' : ''}</label>` : ''}
                ${input}
                ${description ? `<div class="form-description">${description}</div>` : ''}
            </div>
        `;
    },

    getFormData(form, fields) {
        const data = {};

        fields.forEach(field => {
            const { name, type } = field;

            if (type === 'checkbox') {
                const el = form.querySelector(`[name="${name}"]`);
                data[name] = el ? el.checked : false;
            } else if (type === 'unit-select') {
                const checkboxes = form.querySelectorAll(`[name="${name}"]:checked`);
                data[name] = Array.from(checkboxes).map(cb => cb.value);
            } else if (type === 'number' || type === 'range') {
                const el = form.querySelector(`[name="${name}"]`);
                data[name] = el ? parseFloat(el.value) : 0;
            } else if (type !== 'display') {
                const el = form.querySelector(`[name="${name}"]`);
                data[name] = el ? el.value : '';
            }
        });

        return data;
    },

    confirm(message, onConfirm, onCancel) {
        this.show({
            title: 'Confirm',
            content: `<p class="confirm-message">${message}</p>`,
            size: 'small',
            buttons: [
                {
                    label: 'Cancel',
                    onClick: () => {
                        if (onCancel) onCancel();
                        this.close();
                    }
                },
                {
                    label: 'Confirm',
                    primary: true,
                    onClick: () => {
                        if (onConfirm) onConfirm();
                        this.close();
                    }
                }
            ]
        });
    },

    showResult(title, message, isSuccess) {
        this.show({
            title,
            content: `
                <div class="result-container ${isSuccess ? 'result-success' : 'result-failure'}">
                    <div class="result-icon">${isSuccess ? '✓' : '✗'}</div>
                    <p class="result-message">${message}</p>
                </div>
            `,
            size: 'small',
            buttons: [
                { label: 'OK', primary: true, onClick: () => this.close() }
            ]
        });
    },

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'modal-error';
        errorDiv.textContent = message;

        const body = this.activeModal?.querySelector('.modal-body');
        if (body) {
            const existing = body.querySelector('.modal-error');
            if (existing) existing.remove();
            body.insertBefore(errorDiv, body.firstChild);

            setTimeout(() => errorDiv.remove(), 5000);
        }
    },

    showLoading(title = 'Loading...', cancellable = true) {
        this.show({
            title,
            content: `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p>Please wait...</p>
                </div>
            `,
            size: 'small',
            buttons: cancellable ? [
                { label: 'Cancel', onClick: () => this.close() }
            ] : []
        });
    },

    updateContent(selector, content) {
        if (!this.activeModal) return;
        const el = this.activeModal.querySelector(selector);
        if (el) {
            if (typeof content === 'string') {
                el.innerHTML = content;
            } else {
                el.innerHTML = '';
                el.appendChild(content);
            }
        }
    }
};
