//'http://192.168.1.146:9002/system'

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

        // System Tab
        systemServicesLoader: document.getElementById('systemServicesLoader'),
        dockerStatusDot: document.getElementById('dockerStatusDot'),
        dockerStatusText: document.getElementById('dockerStatusText'),
        hwProxyStatusDot: document.getElementById('hwProxyStatusDot'),
        hwProxyStatusText: document.getElementById('hwProxyStatusText'),
        btnDownloadDb: document.getElementById('btnDownloadDb'),
        btnRestartDocker: document.getElementById('btnRestartDocker'),
        btnStopDockerCompose: document.getElementById('btnStopDockerCompose'),
        systemActionStatus: document.getElementById('systemActionStatus'),
        selectJournalSystem: document.getElementById('selectJournalSystem'),
        selectTimeRangeSystem: document.getElementById('selectTimeRangeSystem'),
        btnFetchLogsSystem: document.getElementById('btnFetchLogsSystem'),
        logOutputSystem: document.getElementById('logOutputSystem'),
        btnViewFullLogSystem: document.getElementById('btnViewFullLogSystem'),

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
        fullLogContentSystem: '',
        fullSttyOutput: '',
    },
    Constants: {
        HARDWARE_UPDATE_INTERVAL_MS: 60000, // 60 segundos
    },
    API: {
        _baseUrl: 'https://192.168.1.146:9001/hw_proxy/system',
        async _fetch(url, options = {}) {
            //await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 200));
            //console.log(`Simulando fetch a: ${url}`, options);
            let data = null
            const fetchOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...(options.headers || {})
                },
                ...options
            };
            // Optional: Remove body for GET requests to prevent issues
            if (fetchOptions.method === 'GET' && fetchOptions.body) {
                delete fetchOptions.body;
            }

            try {
                const response = await fetch(url, fetchOptions);

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Fetch error ${response.status}: ${errorText}`);
                }

                // Try to parse as JSON, fallback to text if invalid JSON
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    data = await response.text(); // e.g., for logs
                }
            } catch (error) {
                console.error(`Error fetching ${url}:`, error);
                throw error;
            }

            if (data === null) {
                console.error(`Empty response from ${url}...`);
                throw new Error(`Empty response from ${url}...`);
            }

            if (url.startsWith(`${this._baseUrl}/printer_status`)) {
                return {
                    ...data,
                    serialInfo: {
                        ...data.serialInfo,
                        readStatus: data.serialInfo?.readStatus ? 'OK' : 'Error', writeStatus: data.serialInfo?.writeStatus ? 'OK' : 'Error',
                        sttyOutput: ``
                    }
                };
            } else if (url.startsWith(`${this._baseUrl}/system_status`)) {
                return {
                    dockerRunning: Math.random() > 0.2,
                    hwProxyRunning: Math.random() > 0.3,
                };
            } else if (url.startsWith(`${this._baseUrl}/print_ticket`)) {
                return { success: Math.random() > 0.2 };
            } else if (url.startsWith(`${this._baseUrl}/open_cashdrawer`)) {
                return { success: Math.random() > 0.1 };
            } else if (url.startsWith(`${this._baseUrl}/logs`)) {
                const params = new URLSearchParams(url.split('?')[1]);
                const journal = params.get('journal');
                const timeRange = params.get('time_range');
                const mockLogArray = [
                    `--- Registros para ${journal}, Rango: ${timeRange} ---`,
                    `${new Date().toISOString()} [INFO] Entrada de registro simulada 1.`,
                    ...Array.from({ length: 5 }, (_, i) => `${new Date().toISOString()} [INFO] Más líneas de registro simuladas ${i + 1}.`)
                ];
                return mockLogArray.join('\n');
            } else if (url.startsWith(`${this._baseUrl}/download_db`)) {
                return { success: true, message: 'Descarga de base de datos iniciada.' };
            } else if (url.startsWith(`${this._baseUrl}/restart_docker`)) {
                return { success: true, message: 'Contenedores Docker reiniciados.' };
            } else if (url.startsWith(`${this._baseUrl}/stop_docker_compose`)) {
                return { success: true, message: 'Docker Compose detenido.' };
            } else if (url.startsWith(`${this._baseUrl}/shutdown`) || url.startsWith(`${this._baseUrl}/reboot`)) {
                return { message: 'Comando recibido' };
            }
            throw new Error(`URL de API simulada no reconocida: ${url}`);
        },

        async getPrinterStatus() { try { return await this._fetch(`${this._baseUrl}/printer_status`); } catch (e) { console.error(e); throw e; } },
        async getSystemStatus() { try { return await this._fetch(`${this._baseUrl}/system_status`); } catch (e) { console.error(e); throw e; } },
        async printTicket() { try { const d = await this._fetch(`${this._baseUrl}/print_ticket`); return d.success; } catch (e) { console.error(e); return false; } },
        async openCashDrawer() { try { const d = await this._fetch(`${this._baseUrl}/open_cashdrawer`); return d.success; } catch (e) { console.error(e); return false; } },
        async fetchLogs(journal, timeRange) { try { return await this._fetch(`${this._baseUrl}/logs?journal=${encodeURIComponent(journal)}&time_range=${encodeURIComponent(timeRange)}`); } catch (e) { console.error(e); return `Error: ${e.message}`; } },
        async downloadDb() { try { return await this._fetch(`${this._baseUrl}/download_db`, { method: 'POST' }); } catch (e) { console.error(e); return { success: false, message: 'Error al descargar BD.' }; } },
        async restartDocker() { try { return await this._fetch(`${this._baseUrl}/restart_docker`, { method: 'POST' }); } catch (e) { console.error(e); return { success: false, message: 'Error al reiniciar Docker.' }; } },
        async stopDockerCompose() { try { return await this._fetch(`${this._baseUrl}/stop_docker_compose`, { method: 'POST' }); } catch (e) { console.error(e); return { success: false, message: 'Error al detener Docker Compose.' }; } },
        async shutdown() { try { await this._fetch(`${this._baseUrl}/shutdown`, { method: 'POST' }); return true; } catch (e) { console.error(e); return false; } },
        async reboot() { try { await this._fetch(`${this._baseUrl}/reboot`, { method: 'POST' }); return true; } catch (e) { console.error(e); return false; } }
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
                    App.UI.paperStatusText.textContent = 'OK'; App.UI.paperStatusDot.className = 'status-dot status-green';
                } else if (status.paperLow) {
                    App.UI.paperStatusText.textContent = 'Papel Bajo'; App.UI.paperStatusDot.className = 'status-dot status-yellow';
                } else {
                    App.UI.paperStatusText.textContent = 'Sin Papel / Error'; App.UI.paperStatusDot.className = 'status-dot status-red';
                }
                App.PortInfoManager.display(status.devicePortType, status); // Reutiliza el PortInfoManager
                App.UI.actionStatus.textContent = 'Estado de hardware actualizado.';
            } catch (error) {
                App.UI.actionStatus.textContent = 'Error al actualizar estado de hardware.';
                App.UI.connectionStatusText.textContent = 'Error'; App.UI.connectionStatusDot.className = 'status-dot status-red';
                App.UI.printerStatusText.textContent = 'Error'; App.UI.printerStatusDot.className = 'status-dot status-red';
                App.UI.paperStatusText.textContent = 'Error'; App.UI.paperStatusDot.className = 'status-dot status-red';
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
            this.stopAutoUpdate(); // Clear existing intervals first
            if (!App.State.hardwareAutoUpdateEnabled) {
                this.updateCountdownDisplay();
                return;
            }

            App.State.hardwareTimeUntilNextUpdate = App.Constants.HARDWARE_UPDATE_INTERVAL_MS / 1000;
            this.updateCountdownDisplay();

            App.State.hardwareCountdownIntervalId = setInterval(() => {
                App.State.hardwareTimeUntilNextUpdate--;
                if (App.State.hardwareTimeUntilNextUpdate < 0) {
                    App.State.hardwareTimeUntilNextUpdate = 0; // Prevent negative display briefly
                }
                this.updateCountdownDisplay();
            }, 1000);

            App.State.hardwareUpdateIntervalId = setInterval(async () => {
                await this.fetchAndDisplayStatus();
                // Reset countdown after fetch completes and before next interval starts it again
                clearInterval(App.State.hardwareCountdownIntervalId); // Stop current countdown
                App.State.hardwareTimeUntilNextUpdate = App.Constants.HARDWARE_UPDATE_INTERVAL_MS / 1000; // Reset time
                this.updateCountdownDisplay(); // Show initial time for next cycle
                // Restart countdown for the new cycle
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
                this.fetchAndDisplayStatus(); // Fetch immediately when re-enabled
            } else {
                this.stopAutoUpdate();
            }
        },
        async manualRefresh() {
            await this.fetchAndDisplayStatus();
            if (App.State.hardwareAutoUpdateEnabled) { // Only reset timer if auto-update is on
                this.startAutoUpdate(); // This will clear and restart intervals
            }
        }
    },

    SystemStatusManager: {
        _showLoader() { App.UI.systemServicesLoader.style.display = 'inline-block'; },
        _hideLoader() { App.UI.systemServicesLoader.style.display = 'none'; },
        async fetchAndDisplayStatus() {
            this._showLoader();
            App.UI.systemActionStatus.textContent = 'Actualizando estado de servicios...';
            try {
                const status = await App.API.getSystemStatus();
                App.UI.dockerStatusText.textContent = status.dockerRunning ? 'Activo' : 'Inactivo';
                App.UI.dockerStatusDot.className = `status-dot ${status.dockerRunning ? 'status-green' : 'status-red'}`;
                App.UI.hwProxyStatusText.textContent = status.hwProxyRunning ? 'Activo' : 'Inactivo';
                App.UI.hwProxyStatusDot.className = `status-dot ${status.hwProxyRunning ? 'status-green' : 'status-red'}`;
                App.UI.systemActionStatus.textContent = 'Estado de servicios actualizado.';
            } catch (error) {
                App.UI.systemActionStatus.textContent = 'Error al actualizar estado de servicios.';
                App.UI.dockerStatusText.textContent = 'Error'; App.UI.dockerStatusDot.className = 'status-dot status-red';
                App.UI.hwProxyStatusText.textContent = 'Error'; App.UI.hwProxyStatusDot.className = 'status-dot status-red';
            } finally {
                this._hideLoader();
            }
        }
    },

    StatusManager: { // General orchestrator
        async updateAll() {
            // No auto-update logic here, just initial fetch or general refresh trigger
            await App.HardwareStatusManager.fetchAndDisplayStatus();
            await App.SystemStatusManager.fetchAndDisplayStatus();
        }
    },

    PortInfoManager: { // (Same as previous, just ensure it's called correctly)
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
                contentEl.innerHTML += `<p class="text-muted mt-auto">Información Puerto Red (Aún no implementado)</p>`;
            } else if (portType === 'USB') {
                contentEl.innerHTML += `<p class="text-muted mt-auto">Información Puerto USB (Aún no implementado)</p>`;
            } else {
                contentEl.innerHTML += `<p class="text-muted mt-auto">No hay información detallada del puerto para ${portType || 'desconocido'}.</p>`;
            }
        }
    },
    LogManager: {
        async fetchAndDisplaySystemLogs() {
            App.UI.logOutputSystem.textContent = 'Obteniendo registros del sistema...';
            App.UI.btnViewFullLogSystem.style.display = 'none';
            const journal = App.UI.selectJournalSystem.value;
            const timeRange = App.UI.selectTimeRangeSystem.value;
            try {
                App.State.fullLogContentSystem = await App.API.fetchLogs(journal, timeRange);
                App.UI.logOutputSystem.textContent = App.State.fullLogContentSystem;
                App.UI.btnViewFullLogSystem.style.display = 'inline-block';
            } catch (error) {
                App.UI.logOutputSystem.textContent = `Error al obtener registros: ${error.message}`;
            }
        }
    },
    ModalManager: {
        showConfirmation(message, actionCallback) { App.UI.modalMessage.textContent = message; App.State.currentModalAction = actionCallback; App.UI.confirmationModal.style.display = 'block'; },
        hideConfirmation() { App.UI.confirmationModal.style.display = 'none'; App.State.currentModalAction = null; },
        showContent(title, content) { App.UI.contentModalTitle.textContent = title; App.UI.contentModalBody.textContent = content; App.UI.contentModal.style.display = 'block'; },
        hideContent() { App.UI.contentModal.style.display = 'none'; }
    },
    ActionHandler: {
        async printDummyTicket() {
            App.UI.actionStatus.textContent = 'Imprimiendo ticket de prueba...';
            const success = await App.API.printTicket();
            App.UI.actionStatus.textContent = success ? 'Ticket de prueba impreso correctamente.' : 'Error al imprimir ticket de prueba.';
            App.UI.actionStatus.className = `mt-3 small ${success ? 'text-success' : 'text-danger'}`;
            // No es necesario llamar a updateAll si solo afecta el estado de la impresora que ya se actualiza
        },
        async openCashDrawer() {
            App.UI.actionStatus.textContent = 'Abriendo cajón...';
            const success = await App.API.openCashDrawer();
            App.UI.actionStatus.textContent = success ? 'Cajón abierto correctamente.' : 'Error al abrir cajón.';
            App.UI.actionStatus.className = `mt-3 small ${success ? 'text-success' : 'text-danger'}`;
        },
        async downloadDb() {
            App.UI.systemActionStatus.textContent = 'Iniciando descarga de base de datos...';
            const response = await App.API.downloadDb();
            App.UI.systemActionStatus.textContent = response.message;
            App.UI.systemActionStatus.className = `mt-3 small ${response.success ? 'text-success' : 'text-danger'}`;
        },
        async restartDocker() {
            App.UI.systemActionStatus.textContent = 'Reiniciando contenedores Docker...';
            const response = await App.API.restartDocker();
            App.UI.systemActionStatus.textContent = response.message;
            App.UI.systemActionStatus.className = `mt-3 small ${response.success ? 'text-warning' : 'text-danger'}`;
            await App.SystemStatusManager.fetchAndDisplayStatus(); // Actualizar estado después de la acción
        },
        async stopDockerCompose() {
            App.UI.systemActionStatus.textContent = 'Deteniendo Docker Compose...';
            const response = await App.API.stopDockerCompose();
            App.UI.systemActionStatus.textContent = response.message;
            App.UI.systemActionStatus.className = `mt-3 small ${response.success ? 'text-danger' : 'text-danger'}`;
            await App.SystemStatusManager.fetchAndDisplayStatus(); // Actualizar estado después de la acción
        },
        async shutdownServer() {
            App.ModalManager.hideConfirmation(); App.UI.actionStatus.textContent = 'Enviando comando de apagado...';
            const success = await App.API.shutdown();
            App.UI.actionStatus.textContent = success ? 'Comando de apagado enviado.' : 'Error al enviar comando de apagado.';
            App.UI.actionStatus.className = `mt-3 small ${success ? 'text-info' : 'text-danger'}`;
        },
        async rebootServer() {
            App.ModalManager.hideConfirmation(); App.UI.actionStatus.textContent = 'Enviando comando de reinicio...';
            const success = await App.API.reboot();
            App.UI.actionStatus.textContent = success ? 'Comando de reinicio enviado.' : 'Error al enviar comando de reinicio.';
            App.UI.actionStatus.className = `mt-3 small ${success ? 'text-info' : 'text-danger'}`;
        }
    },
    init() {
        // Hardware Tab
        App.UI.autoUpdateHardwareSwitch.addEventListener('change', App.HardwareStatusManager.toggleAutoUpdate.bind(App.HardwareStatusManager));
        App.UI.btnRefreshHardware.addEventListener('click', App.HardwareStatusManager.manualRefresh.bind(App.HardwareStatusManager));
        App.UI.btnPrintDummy.addEventListener('click', App.ActionHandler.printDummyTicket);
        App.UI.btnOpenCashDrawer.addEventListener('click', App.ActionHandler.openCashDrawer);

        // System Tab
        App.UI.btnDownloadDb.addEventListener('click', App.ActionHandler.downloadDb);
        App.UI.btnRestartDocker.addEventListener('click', App.ActionHandler.restartDocker);
        App.UI.btnStopDockerCompose.addEventListener('click', App.ActionHandler.stopDockerCompose);
        App.UI.btnFetchLogsSystem.addEventListener('click', App.LogManager.fetchAndDisplaySystemLogs);
        App.UI.btnViewFullLogSystem.addEventListener('click', () =>
            App.ModalManager.showContent(App.State.fullLogContentSystem ? 'Registro Completo del Sistema' : 'Registro del Sistema', App.State.fullLogContentSystem || 'No hay contenido de registro.')
        );

        // Global
        App.UI.btnShutdown.addEventListener('click', () => App.ModalManager.showConfirmation('¿Está seguro que desea apagar el servidor?', App.ActionHandler.shutdownServer));
        App.UI.btnReboot.addEventListener('click', () => App.ModalManager.showConfirmation('¿Está seguro que desea reiniciar el servidor?', App.ActionHandler.rebootServer));

        App.UI.modalConfirmBtn.addEventListener('click', () => { if (App.State.currentModalAction) App.State.currentModalAction(); });
        App.UI.modalCancelBtn.addEventListener('click', App.ModalManager.hideConfirmation);
        App.UI.contentModalCloseBtn.addEventListener('click', App.ModalManager.hideContent);
        window.onclick = (event) => {
            if (event.target == App.UI.confirmationModal) App.ModalManager.hideConfirmation();
            if (event.target == App.UI.contentModal) App.ModalManager.hideContent();
        };

        // Initial Load & Start Auto-Update for Hardware
        App.SystemStatusManager.fetchAndDisplayStatus(); // Fetch system status once
        App.HardwareStatusManager.fetchAndDisplayStatus(); // Initial fetch for hardware
        App.HardwareStatusManager.startAutoUpdate(); // Start auto-update cycle for hardware

        App.UI.logOutputSystem.textContent = 'Aún no se han obtenido registros.';
        App.UI.portInfoContent.innerHTML = '<p class="text-muted">Obteniendo información del puerto...</p>';
        App.UI.actionStatus.textContent = ''; // Clear initial messages
        App.UI.systemActionStatus.textContent = '';
    }
};
document.addEventListener('DOMContentLoaded', App.init);