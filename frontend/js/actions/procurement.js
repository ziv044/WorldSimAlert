// Procurement Actions
const ProcurementActions = {
    catalog: null,
    inventory: null,

    async loadCatalog() {
        if (!this.catalog) {
            const result = await api.getWeaponsCatalog();
            this.catalog = result.catalog || {};
        }
        return this.catalog;
    },

    getCatalogOptions() {
        if (!this.catalog) return [];
        return Object.entries(this.catalog).map(([id, weapon]) => ({
            value: id,
            label: `${weapon.name} (${weapon.category})`
        }));
    },

    async showPurchase() {
        Modal.showLoading('Loading weapons catalog...');

        try {
            await this.loadCatalog();
            Modal.close();

            if (Object.keys(this.catalog).length === 0) {
                Modal.show({
                    title: 'Buy Weapons',
                    content: '<p class="empty-state">No weapons available for purchase.</p>',
                    size: 'small',
                    buttons: [{ label: 'Close', onClick: () => Modal.close() }]
                });
                return;
            }

            Modal.showForm({
                title: 'Buy Weapons',
                size: 'large',
                fields: [
                    {
                        name: 'weapon_id',
                        type: 'select',
                        label: 'Weapon System',
                        options: this.getCatalogOptions(),
                        onChange: (value, modal) => this.updateWeaponPreview(value, modal)
                    },
                    {
                        name: 'quantity',
                        type: 'number',
                        label: 'Quantity',
                        min: 1,
                        max: 100,
                        step: 1,
                        defaultValue: 1
                    },
                    {
                        name: 'preview',
                        type: 'display',
                        label: 'Details',
                        defaultValue: 'Select a weapon to see details'
                    }
                ],
                submitLabel: 'Purchase',
                onSubmit: async (data) => {
                    // First check eligibility
                    const check = await api.checkPurchase(App.countryCode, {
                        weapon_id: data.weapon_id,
                        quantity: data.quantity
                    });

                    if (!check.eligible) {
                        throw new Error(check.reason || 'Purchase not eligible');
                    }

                    // Proceed with purchase
                    const result = await api.purchaseWeapon(App.countryCode, {
                        weapon_id: data.weapon_id,
                        quantity: data.quantity
                    });

                    if (result.success) {
                        const weapon = this.catalog[data.weapon_id];
                        App.showNotification(`Ordered ${data.quantity}x ${weapon?.name || data.weapon_id}`, 'success');
                    } else {
                        throw new Error(result.error || 'Purchase failed');
                    }
                }
            });

        } catch (error) {
            Modal.close();
            Modal.showResult('Error', 'Failed to load catalog: ' + error.message, false);
        }
    },

    updateWeaponPreview(weaponId, modal) {
        const weapon = this.catalog[weaponId];
        if (!weapon) return;

        const preview = `
            <strong>${weapon.name}</strong><br>
            Category: ${weapon.category}<br>
            Unit Cost: $${(weapon.unit_cost_millions || 0).toFixed(1)}M<br>
            ${weapon.description || ''}
        `;

        Modal.updateContent('#preview', preview);
    },

    async showSell() {
        // Load current inventory
        Modal.showLoading('Loading inventory...');

        try {
            const unitsResult = await api.getUnits(App.countryCode);
            const units = unitsResult.units || [];

            Modal.close();

            // Group units by type for selling
            const inventory = {};
            units.forEach(unit => {
                const type = unit.unit_type || 'Unknown';
                if (!inventory[type]) {
                    inventory[type] = { count: 0, name: type };
                }
                inventory[type].count += unit.quantity || 1;
            });

            if (Object.keys(inventory).length === 0) {
                Modal.show({
                    title: 'Sell Weapons',
                    content: '<p class="empty-state">No weapons in inventory to sell.</p>',
                    size: 'small',
                    buttons: [{ label: 'Close', onClick: () => Modal.close() }]
                });
                return;
            }

            const inventoryOptions = Object.entries(inventory).map(([type, data]) => ({
                value: type,
                label: `${type} (${data.count} available)`
            }));

            Modal.showForm({
                title: 'Sell Weapons',
                fields: [
                    {
                        name: 'weapon_model',
                        type: 'select',
                        label: 'Weapon to Sell',
                        options: inventoryOptions
                    },
                    {
                        name: 'quantity',
                        type: 'number',
                        label: 'Quantity',
                        min: 1,
                        max: 100,
                        step: 1,
                        defaultValue: 1
                    },
                    {
                        name: 'buyer_country',
                        type: 'text',
                        label: 'Buyer Country Code',
                        placeholder: 'e.g., USA, DEU, FRA'
                    }
                ],
                submitLabel: 'Sell',
                onSubmit: async (data) => {
                    const result = await api.sellWeapon(App.countryCode, data);
                    if (result.success) {
                        App.showNotification(`Sold ${data.quantity}x ${data.weapon_model}`, 'success');
                        UnitsPanel.load && UnitsPanel.load(App.countryCode);
                    } else {
                        throw new Error(result.error || 'Sale failed');
                    }
                }
            });

        } catch (error) {
            Modal.close();
            Modal.showResult('Error', 'Failed to load inventory: ' + error.message, false);
        }
    },

    async showOrders() {
        Modal.showLoading('Loading orders...');

        try {
            const result = await api.getProcurementOrders(App.countryCode);
            const orders = result.orders || [];

            Modal.close();

            if (orders.length === 0) {
                Modal.show({
                    title: 'Active Orders',
                    content: '<p class="empty-state">No active procurement orders.</p>',
                    size: 'small',
                    buttons: [{ label: 'Close', onClick: () => Modal.close() }]
                });
                return;
            }

            Modal.show({
                title: 'Active Orders',
                content: this.renderOrdersList(orders),
                size: 'large',
                buttons: [{ label: 'Close', onClick: () => Modal.close() }]
            });

            // Wire up cancel buttons
            document.querySelectorAll('.order-cancel-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const orderId = e.target.dataset.orderId;
                    this.cancelOrder(orderId);
                });
            });

        } catch (error) {
            Modal.close();
            Modal.showResult('Error', 'Failed to load orders: ' + error.message, false);
        }
    },

    renderOrdersList(orders) {
        return `
            <div class="orders-list">
                ${orders.map(order => `
                    <div class="order-item">
                        <div class="order-info">
                            <div class="order-name">${order.weapon_id || 'Unknown'} x${order.quantity || 1}</div>
                            <div class="order-status">Status: ${order.status || 'processing'}</div>
                            ${order.delivery_date ? `<div class="order-eta">Delivery: ${order.delivery_date}</div>` : ''}
                            ${order.progress !== undefined ? `
                                <div class="order-progress-container">
                                    <div class="order-progress-bar">
                                        <div class="order-progress-fill" style="width: ${order.progress}%"></div>
                                    </div>
                                    <span class="order-progress-text">${order.progress.toFixed(0)}%</span>
                                </div>
                            ` : ''}
                        </div>
                        <button class="btn btn-danger btn-sm order-cancel-btn" data-order-id="${order.order_id || order.id}">
                            Cancel
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    },

    async cancelOrder(orderId) {
        Modal.confirm('Cancel this order? A cancellation fee may apply.', async () => {
            try {
                const result = await api.cancelProcurementOrder(App.countryCode, orderId);
                if (result.success) {
                    App.showNotification('Order cancelled', 'success');
                    this.showOrders(); // Refresh list
                } else {
                    throw new Error(result.error || 'Failed to cancel order');
                }
            } catch (error) {
                Modal.showResult('Error', error.message, false);
            }
        });
    }
};
