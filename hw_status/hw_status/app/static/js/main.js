const App = {
    UI: {
        // Hardware Tab
        autoUpdateHardwareSwitch: document.getElementById('autoUpdateHardwareSwitch'),
        hardwareUpdateCountdown: document.getElementById('hardwareUpdateCountdown'),
        btnRefreshHardware: document.getElementById('btnRefreshHardware'),
        deviceStatusLoader: document.getElementById('deviceStatusLoader'),
        portInfoLoader: document.getElementById('portInfoLoader'),
        btnPrintDummy: document.getElementById('btnPrintDummy'),
        btnOpenCashDrawer: document.getElementById('btnOpenCashDrawer'),
        actionStatus: document.getElementById('actionStatus'),
        connectionStatusDot: document.getElementById('connectionStatusDot'),
        connectionStatusText: document.getElementById('connectionStatusText'),
        printerStatusDot: document.getElementById('printerStatusDot'),
        printerStatusText: document.getElementById('printerStatusText'),
        paperStatusDot: document.getElementById('paperStatusDot'),
        paperStatusText: document.getElementById('paperStatusText'),
        portInfoContent: document.getElementById('portInfoContent'),

        // Service Logs Panel
        selectLogService: document.getElementById('selectLogService'),
        btnRefreshServiceLogs: document.getElementById('btnRefreshServiceLogs'),
        btnExpandServiceLogs: document.getElementById('btnExpandServiceLogs'),
        logOutputService: document.getElementById('logOutputService'),

        // Services Status Panel
        servicesStatusGrid: document.getElementById('servicesStatusGrid'),
        servicesLastUpdate: document.getElementById('servicesLastUpdate'),
        btnRefreshServices: document.getElementById('btnRefreshServices'),

        // Global
        btnShutdown: document.getElementById('btn-shutdown'),
        btnReboot: document.getElementById('btn-reboot'),
        confirmationModal: document.getElementById('confirmationModal'),
        modalMessage: document.getElementById('modalMessage'),
        modalConfirmBtn: document.getElementById('modalConfirmBtn'),
        modalCancelBtn: document.getElementById('modalCancelBtn'),
        contentModal: document.getElementById('contentModal'),
        contentModalTitle: document.getElementById('contentModalTitle'),
        contentModalBody: document.getElementById('contentModalBody'),
        contentModalCloseBtn: document.getElementById('contentModalCloseBtn'),
    },
    State: {
        hardwareUpdateIntervalId: null,
        hardwareAutoUpdateEnabled: true,
        hardwareTimeUntilNextUpdate: 60,
        hardwareCountdownIntervalId: null,
        isHardwareRefreshing: false,
        currentModalAction: null,
        fullLogContentService: '',
        fullSttyOutput: '',
    },
    Constants: {
        HARDWARE_UPDATE_INTERVAL_MS: 60000,
    },
    API: {
        _baseUrl: window.HW_PROXY_BASE_URL || 'http://localhost:9002/hw_proxy/system',
        async _fetch(url, options = {}) {
            const fetchOptions = {
                method: 'GET',
                headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
                ...options,
            };
            if (fetchOptions.method === 'GET' && fetchOptions.body) delete fetchOptions.body;

            const response = await fetch(url, fetchOptions);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Fetch error ${response.status}: ${errorText}`);
            }

            const contentType = response.headers.get('content-type');
            const data = (contentType && contentType.includes('application/json'))
                ? await response.json()
                : await response.text();

            // Transform printer_status response: convert boolean read/write flags to strings
            if (url.startsWith(`${this._baseUrl}/printer_status`) && typeof data === 'object') {
                return {
                    ...data,
                    serialInfo: {
                        ...data.serialInfo,
                        readStatus: data.serialInfo?.readStatus ? 'OK' : 'Error',
                        writeStatus: data.serialInfo?.writeStatus ? 'OK' : 'Error',
                        sttyOutput: '',
                    },
                };
            }
            return data;
        },

        async getPrinterStatus() {
            try { return await this._fetch(`${this._baseUrl}/printer_status`); }
            catch (e) { console.error(e); throw e; }
        },
        async printTicket() {
            try { const d = await this._fetch(`${this._baseUrl}/print_ticket`); return d.success; }
            catch (e) { console.error(e); return false; }
        },
        async openCashDrawer() {
            try { const d = await this._fetch(`${this._baseUrl}/open_cashdrawer`); return d.success; }
            catch (e) { console.error(e); return false; }
        },
        async fetchServiceLogs(service, level = 'warning', lines = 100) {
            try {
                return await this._fetch(
                    `${this._baseUrl}/logs?service=${encodeURIComponent(service)}&level=${encodeURIComponent(level)}&lines=${lines}`
                );
            } catch (e) { console.error(e); return `Error: ${e.message}`; }
        },
        async getServicesStatus() {
            try { return await this._fetch(`${this._baseUrl}/services/status`); }
            catch (e) { console.error(e); return null; }
        },
        async shutdown() {
            try { await this._fetch(`${this._baseUrl}/shutdown`, { method: 'POST' }); return true; }
            catch (e) { console.error(e); return false; }
        },
        async reboot() {
            try { await this._fetch(`${this._baseUrl}/reboot`, { method: 'POST' }); return true; }
            catch (e) { console.error(e); return false; }
        },
    },

    HardwareStatusManager: {
        _showLoader() {
            App.UI.deviceStatusLoader.style.display = 'inline-block';
            App.UI.portInfoLoader.style.display = 'inline-block';
            App.UI.btnRefreshHardware.disabled = true;
        },
        _hideLoader() {
            App.UI.deviceStatusLoader.style.display = 'none';
            App.UI.portInfoLoader.style.display = 'none';
            App.UI.btnRefreshHardware.disabled = false;
        },
        async fetchAndDisplayStatus() {
            if (App.State.isHardwareRefreshing) return;
            App.State.isHardwareRefreshing = true;
            this._showLoader();
            App.UI.actionStatus.textContent = 'Actualizando estado del hardware...';
            try {
                const status = await App.API.getPrinterStatus();
                App.UI.connectionStatusText.textContent = status.connected ? 'Conectado' : 'Desconectado';
                App.UI.connectionStatusDot.className = `status-dot ${status.connected ? 'status-green' : 'status-red'}`;
                App.UI.printerStatusText.textContent = status.printerOnline ? 'En línea' : 'Fuera de línea';
                App.UI.printerStatusDot.className = `status-dot ${status.printerOnline ? 'status-green' : 'status-red'}`;
                if (status.paperOk) {
                    App.UI.paperStatusText.textContent = 'OK';
                    App.UI.paperStatusDot.className = 'status-dot status-green';
                } else if (status.paperLow) {
                    App.UI.paperStatusText.textContent = 'Papel Bajo';
                    App.UI.paperStatusDot.className = 'status-dot status-yellow';
                } else {
                    App.UI.paperStatusText.textContent = 'Sin Papel / Error';
                    App.UI.paperStatusDot.className = 'status-dot status-red';
                }
                App.PortInfoManager.display(status.devicePortType, status);
                App.UI.actionStatus.textContent = 'Estado de hardware actualizado.';
            } catch (error) {
                App.UI.actionStatus.textContent = 'Error al actualizar estado de hardware.';
                App.UI.connectionStatusText.textContent = 'Error';
                App.UI.connectionStatusDot.className = 'status-dot status-red';
                App.UI.printerStatusText.textContent = 'Error';
                App.UI.printerStatusDot.className = 'status-dot status-red';
                App.UI.paperStatusText.textContent = 'Error';
                App.UI.paperStatusDot.className = 'status-dot status-red';
                if (App.UI.portInfoContent) App.UI.portInfoContent.innerHTML = '<p class="text-danger">No se pudo cargar la información del puerto.</p>';
            } finally {
                this._hideLoader();
                App.State.isHardwareRefreshing = false;
            }
        },
        updateCountdownDisplay() {
            if (App.State.hardwareAutoUpdateEnabled && App.State.hardwareTimeUntilNextUpdate > 0) {
                App.UI.hardwareUpdateCountdown.textContent = `Próxima act.: ${App.State.hardwareTimeUntilNextUpdate}s`;
            } else if (!App.State.hardwareAutoUpdateEnabled) {
                App.UI.hardwareUpdateCountdown.textContent = 'Auto-actualización pausada';
            } else {
                App.UI.hardwareUpdateCountdown.textContent = 'Actualizando...';
            }
        },
        startAutoUpdate() {
            this.stopAutoUpdate();
            if (!App.State.hardwareAutoUpdateEnabled) { this.updateCountdownDisplay(); return; }
            App.State.hardwareTimeUntilNextUpdate = App.Constants.HARDWARE_UPDATE_INTERVAL_MS / 1000;
            this.updateCountdownDisplay();
            App.State.hardwareCountdownIntervalId = setInterval(() => {
                App.State.hardwareTimeUntilNextUpdate--;
                if (App.State.hardwareTimeUntilNextUpdate < 0) App.State.hardwareTimeUntilNextUpdate = 0;
                this.updateCountdownDisplay();
            }, 1000);
            App.State.hardwareUpdateIntervalId = setInterval(async () => {
                await this.fetchAndDisplayStatus();
                clearInterval(App.State.hardwareCountdownIntervalId);
                App.State.hardwareTimeUntilNextUpdate = App.Constants.HARDWARE_UPDATE_INTERVAL_MS / 1000;
                this.updateCountdownDisplay();
                App.State.hardwareCountdownIntervalId = setInterval(() => {
                    App.State.hardwareTimeUntilNextUpdate--;
                    if (App.State.hardwareTimeUntilNextUpdate < 0) App.State.hardwareTimeUntilNextUpdate = 0;
                    this.updateCountdownDisplay();
                }, 1000);
            }, App.Constants.HARDWARE_UPDATE_INTERVAL_MS);
        },
        stopAutoUpdate() {
            clearInterval(App.State.hardwareUpdateIntervalId);
            clearInterval(App.State.hardwareCountdownIntervalId);
            App.State.hardwareUpdateIntervalId = null;
            App.State.hardwareCountdownIntervalId = null;
            this.updateCountdownDisplay();
        },
        toggleAutoUpdate(event) {
            App.State.hardwareAutoUpdateEnabled = event.target.checked;
            if (App.State.hardwareAutoUpdateEnabled) {
                this.startAutoUpdate();
                this.fetchAndDisplayStatus();
            } else {
                this.stopAutoUpdate();
            }
        },
        async manualRefresh() {
            await this.fetchAndDisplayStatus();
            if (App.State.hardwareAutoUpdateEnabled) this.startAutoUpdate();
        },
    },

    PortInfoManager: {
        display(portType, statusData) {
            const contentEl = App.UI.portInfoContent;
            contentEl.innerHTML = '';
            const title = document.createElement('h3');
            title.className = 'h6 mb-3 text-secondary';
            title.textContent = `Tipo de Puerto: ${portType}`;
            contentEl.appendChild(title);
            if (portType === 'SERIAL' && statusData.serialInfo) {
                const info = statusData.serialInfo;
                const listGroup = document.createElement('ul');
                listGroup.className = 'list-group list-group-flush mb-3';
                const addDetail = (term, definition, statusVal = null) => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item d-flex justify-content-between align-items-center small p-2';
                    let statusIndicator = '';
                    if (statusVal === 'OK') statusIndicator = '<span class="status-dot status-green ms-2"></span>';
                    else if (statusVal === 'Error') statusIndicator = '<span class="status-dot status-red ms-2"></span>';
                    li.innerHTML = `${term}: <strong class="text-dark">${definition}</strong> ${statusIndicator}`;
                    listGroup.appendChild(li);
                };
                addDetail('Archivo Dispositivo', info.devfile);
                addDetail('Estado Lectura', info.readStatus, info.readStatus);
                addDetail('Estado Escritura', info.writeStatus, info.writeStatus);
                contentEl.appendChild(listGroup);
                const configContainer = document.createElement('div');
                configContainer.className = 'mt-auto d-flex flex-column flex-grow-1 stty-output-container';
                const configHeaderDiv = document.createElement('div');
                configHeaderDiv.className = 'd-flex justify-content-between align-items-center mb-2';
                const configTitleHeader = document.createElement('h4');
                configTitleHeader.className = 'h6 mb-0 text-secondary';
                configTitleHeader.textContent = 'Configuración Puerto Serie (stty):';
                configHeaderDiv.appendChild(configTitleHeader);
                const btnViewFullStty = document.createElement('button');
                btnViewFullStty.className = 'btn btn-sm btn-outline-secondary';
                btnViewFullStty.innerHTML = '<i class="fas fa-expand-arrows-alt me-1"></i>Expandir';
                btnViewFullStty.onclick = () => {
                    App.State.fullSttyOutput = `Baudios: ${info.baudrate}\nTamaño Byte: ${info.bytesize}\nParidad: ${info.parity}\nBits Parada: ${info.stopbits}\nTiempo Espera: ${info.timeout}s\nControl Flujo DSR/DTR: ${info.dsrdtr}\nPerfil: ${info.profile}\n\nSalida stty Completa:\n${info.sttyOutput || 'No disponible'}`;
                    App.ModalManager.showContent('Configuración Completa Puerto Serie (stty)', App.State.fullSttyOutput);
                };
                configHeaderDiv.appendChild(btnViewFullStty);
                configContainer.appendChild(configHeaderDiv);
                const sttyPre = document.createElement('pre');
                sttyPre.className = 'stty-output-preview';
                sttyPre.textContent = `Baudios: ${info.baudrate}\nTamaño Byte: ${info.bytesize}\nParidad: ${info.parity}\nBits Parada: ${info.stopbits}\nTiempo Espera: ${info.timeout}s\nDSR/DTR: ${info.dsrdtr}\nPerfil: ${info.profile}\n\nSalida stty (vista previa):\n${(info.sttyOutput || 'No disponible').substring(0, 150)}...`;
                configContainer.appendChild(sttyPre);
                contentEl.appendChild(configContainer);
            } else if (portType === 'NETWORK') {
                contentEl.innerHTML += '<p class="text-muted mt-auto">Información Puerto Red (Aún no implementado)</p>';
            } else if (portType === 'USB') {
                contentEl.innerHTML += '<p class="text-muted mt-auto">Información Puerto USB (Aún no implementado)</p>';
            } else {
                contentEl.innerHTML += `<p class="text-muted mt-auto">No hay información detallada del puerto para ${portType || 'desconocido'}.</p>`;
            }
        },
    },

    ServiceLogsManager: {
        async fetchAndDisplay() {
            const pre = App.UI.logOutputService;
            const expandBtn = App.UI.btnExpandServiceLogs;
            const refreshBtn = App.UI.btnRefreshServiceLogs;
            const service = App.UI.selectLogService.value;
            pre.textContent = `Obteniendo registros de ${service}...`;
            expandBtn.style.display = 'none';
            refreshBtn.disabled = true;
            try {
                const logs = await App.API.fetchServiceLogs(service);
                App.State.fullLogContentService = logs;
                pre.textContent = logs;
                expandBtn.style.display = 'inline-block';
            } catch (e) {
                pre.textContent = `Error: ${e.message}`;
                App.State.fullLogContentService = '';
            } finally {
                refreshBtn.disabled = false;
            }
        },
        expandLogs() {
            const service = App.UI.selectLogService ? App.UI.selectLogService.value : 'servicio';
            App.ModalManager.showContent(
                `Registros: ${service}`,
                App.State.fullLogContentService || '[Sin contenido]',
                true
            );
        },
    },

    ServicesStatusManager: {
        _render(services) {
            const grid = App.UI.servicesStatusGrid;
            if (!services || !services.length) {
                grid.innerHTML = '<p class="text-muted small">No se encontraron servicios.</p>';
                return;
            }
            grid.innerHTML = services.map(svc => {
                const dotClass = svc.active ? 'status-green'
                    : (svc.status === 'unknown' || svc.status === 'not found') ? 'status-gray'
                    : 'status-red';
                const typeBadge = svc.type === 'docker'
                    ? '<span class="badge bg-info text-dark ms-1" style="font-size:0.65rem;">docker</span>'
                    : '<span class="badge bg-secondary ms-1" style="font-size:0.65rem;">systemd</span>';
                return `<div class="service-status-item">
                    <span class="status-dot ${dotClass}"></span>
                    <span class="service-item-name">${svc.name}</span>
                    ${typeBadge}
                    <span class="service-item-status">${svc.status}</span>
                </div>`;
            }).join('');
            App.UI.servicesLastUpdate.textContent = `Actualizado: ${new Date().toLocaleTimeString()}`;
        },
        async fetchAndDisplay() {
            const grid = App.UI.servicesStatusGrid;
            const btn = App.UI.btnRefreshServices;
            btn.disabled = true;
            grid.innerHTML = '<p class="text-muted small">Actualizando...</p>';
            try {
                const data = await App.API.getServicesStatus();
                if (data) {
                    this._render(data.services);
                } else {
                    grid.innerHTML = '<p class="text-danger small">Error al obtener estado de servicios.</p>';
                }
            } catch (e) {
                grid.innerHTML = `<p class="text-danger small">Error: ${e.message}</p>`;
            } finally {
                btn.disabled = false;
            }
        },
    },

    ModalManager: {
        showConfirmation(message, actionCallback) {
            App.UI.modalMessage.textContent = message;
            App.State.currentModalAction = actionCallback;
            App.UI.confirmationModal.style.display = 'block';
        },
        hideConfirmation() {
            App.UI.confirmationModal.style.display = 'none';
            App.State.currentModalAction = null;
        },
        showContent(title, content, wide = false) {
            App.UI.contentModalTitle.textContent = title;
            App.UI.contentModalBody.textContent = content;
            App.UI.contentModal.style.display = 'block';
            App.UI.contentModal.querySelector('.modal-custom-content').classList.toggle('modal-xl-custom', wide);
            App.UI.contentModalBody.classList.toggle('service-log-expanded', wide);
        },
        hideContent() {
            App.UI.contentModal.style.display = 'none';
            App.UI.contentModal.querySelector('.modal-custom-content').classList.remove('modal-xl-custom');
            App.UI.contentModalBody.classList.remove('service-log-expanded');
        },
    },

    ActionHandler: {
        async printDummyTicket() {
            App.UI.actionStatus.textContent = 'Imprimiendo ticket de prueba...';
            const success = await App.API.printTicket();
            App.UI.actionStatus.textContent = success ? 'Ticket de prueba impreso correctamente.' : 'Error al imprimir ticket de prueba.';
            App.UI.actionStatus.className = `mt-3 small ${success ? 'text-success' : 'text-danger'}`;
        },
        async openCashDrawer() {
            App.UI.actionStatus.textContent = 'Abriendo cajón...';
            const success = await App.API.openCashDrawer();
            App.UI.actionStatus.textContent = success ? 'Cajón abierto correctamente.' : 'Error al abrir cajón.';
            App.UI.actionStatus.className = `mt-3 small ${success ? 'text-success' : 'text-danger'}`;
        },
        async shutdownServer() {
            App.ModalManager.hideConfirmation();
            App.UI.actionStatus.textContent = 'Enviando comando de apagado...';
            const success = await App.API.shutdown();
            App.UI.actionStatus.textContent = success ? 'Comando de apagado enviado.' : 'Error al enviar comando de apagado.';
            App.UI.actionStatus.className = `mt-3 small ${success ? 'text-info' : 'text-danger'}`;
        },
        async rebootServer() {
            App.ModalManager.hideConfirmation();
            App.UI.actionStatus.textContent = 'Enviando comando de reinicio...';
            const success = await App.API.reboot();
            App.UI.actionStatus.textContent = success ? 'Comando de reinicio enviado.' : 'Error al enviar comando de reinicio.';
            App.UI.actionStatus.className = `mt-3 small ${success ? 'text-info' : 'text-danger'}`;
        },
    },

    init() {
        // Hardware Tab
        App.UI.autoUpdateHardwareSwitch.addEventListener('change', App.HardwareStatusManager.toggleAutoUpdate.bind(App.HardwareStatusManager));
        App.UI.btnRefreshHardware.addEventListener('click', App.HardwareStatusManager.manualRefresh.bind(App.HardwareStatusManager));
        App.UI.btnPrintDummy.addEventListener('click', App.ActionHandler.printDummyTicket);
        App.UI.btnOpenCashDrawer.addEventListener('click', App.ActionHandler.openCashDrawer);

        // Service Logs Panel
        App.UI.btnRefreshServiceLogs.addEventListener('click', () => App.ServiceLogsManager.fetchAndDisplay());
        App.UI.btnExpandServiceLogs.addEventListener('click', () => App.ServiceLogsManager.expandLogs());

        // Services Status Panel
        App.UI.btnRefreshServices.addEventListener('click', () => App.ServicesStatusManager.fetchAndDisplay());

        // Global modals
        App.UI.btnShutdown.addEventListener('click', () => App.ModalManager.showConfirmation('¿Está seguro que desea apagar el servidor?', App.ActionHandler.shutdownServer));
        App.UI.btnReboot.addEventListener('click', () => App.ModalManager.showConfirmation('¿Está seguro que desea reiniciar el servidor?', App.ActionHandler.rebootServer));
        App.UI.modalConfirmBtn.addEventListener('click', () => { if (App.State.currentModalAction) App.State.currentModalAction(); });
        App.UI.modalCancelBtn.addEventListener('click', App.ModalManager.hideConfirmation);
        App.UI.contentModalCloseBtn.addEventListener('click', App.ModalManager.hideContent);
        window.onclick = (event) => {
            if (event.target === App.UI.confirmationModal) App.ModalManager.hideConfirmation();
            if (event.target === App.UI.contentModal) App.ModalManager.hideContent();
        };

        // Initial load
        App.HardwareStatusManager.fetchAndDisplayStatus();
        App.HardwareStatusManager.startAutoUpdate();
        App.ServicesStatusManager.fetchAndDisplay();

        App.UI.portInfoContent.innerHTML = '<p class="text-muted">Obteniendo información del puerto...</p>';
        App.UI.actionStatus.textContent = '';
    },
};

document.addEventListener('DOMContentLoaded', App.init);
