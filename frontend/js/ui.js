/**
 * InferOps - UI Management Module
 *
 * This module is responsible for all direct manipulations of the DOM.
 * It handles updating the dashboard, rendering alerts, managing modals,
 * and reflecting the application's state on the user interface.
 */

import { cpuChart, gpuChart, memoryChart, gpuMemoryChart } from './charts.js';

const nodeStatusContainer = document.getElementById('node-status-container');
const alertsContainer = document.getElementById('alerts-container');
const modelSelect = document.getElementById('model-select');

/**
 * Renders the status cards for each compute node.
 * @param {Array} nodes - An array of node status objects from the API.
 */
function updateNodeCards(nodes) {
    if (!nodeStatusContainer) return;

    // Create a map for quick lookups
    const nodeMap = new Map(nodes.map(node => [node.id, node]));
    
    // Update existing cards or create new ones
    for (const node of nodes) {
        let card = document.getElementById(`node-card-${node.id}`);
        if (!card) {
            card = createNodeCard(node);
            nodeStatusContainer.appendChild(card);
        }
        updateCardContent(card, node);
    }

    // Remove cards for nodes that are no longer present
    for (const child of nodeStatusContainer.children) {
        const nodeId = parseInt(child.id.split('-')[2]);
        if (!nodeMap.has(nodeId)) {
            child.remove();
        }
    }
}

/**
 * Creates the initial HTML structure for a node status card.
 * @param {Object} node - The node status object.
 * @returns {HTMLElement} The created card element.
 */
function createNodeCard(node) {
    const card = document.createElement('div');
    card.id = `node-card-${node.id}`;
    card.className = 'p-4 rounded-lg shadow-md transition-all duration-300';
    card.innerHTML = `
        <div class="flex justify-between items-center mb-2">
            <h3 class="text-lg font-bold"></h3>
            <div class="status-indicator w-4 h-4 rounded-full"></div>
        </div>
        <p class="text-sm text-gray-400 mb-2 cpu-model"></p>
        <div class="grid grid-cols-2 gap-2 text-sm">
            <div><span class="font-semibold">GPU:</span> <span class="gpu-util">N/A</span>%</div>
            <div><span class="font-semibold">GPU Mem:</span> <span class="gpu-mem">N/A</span>%</div>
            <div><span class="font-semibold">CPU:</span> <span class="cpu-util">N/A</span>%</div>
            <div><span class="font-semibold">RAM:</span> <span class="ram-util">N/A</span>%</div>
            <div><span class="font-semibold">Temp:</span> <span class="gpu-temp">N/A</span>°C</div>
            <div class="font-semibold busy-status"></div>
        </div>
    `;
    return card;
}

/**
 * Updates the content of a specific node card with new data.
 * @param {HTMLElement} card - The card element to update.
 * @param {Object} node - The new node status object.
 */
function updateCardContent(card, node) {
    const nameEl = card.querySelector('h3');
    const indicatorEl = card.querySelector('.status-indicator');
    const cpuModelEl = card.querySelector('.cpu-model');
    const gpuUtilEl = card.querySelector('.gpu-util');
    const gpuMemEl = card.querySelector('.gpu-mem');
    const cpuUtilEl = card.querySelector('.cpu-util');
    const ramUtilEl = card.querySelector('.ram-util');
    const gpuTempEl = card.querySelector('.gpu-temp');
    const busyStatusEl = card.querySelector('.busy-status');

    nameEl.textContent = node.name;
    cpuModelEl.textContent = node.cpu_model || 'Fetching...';

    if (node.online) {
        indicatorEl.classList.remove('bg-red-500', 'animate-pulse');
        indicatorEl.classList.add('bg-green-500');
        card.classList.remove('bg-gray-700', 'border-gray-600');
        card.classList.add('bg-gray-800', 'border-gray-700');

        const metrics = node.metrics;
        if (metrics) {
            gpuUtilEl.textContent = metrics.gpu?.utilization_percent?.toFixed(1) ?? 'N/A';
            gpuMemEl.textContent = metrics.gpu?.memory_usage_percent?.toFixed(1) ?? 'N/A';
            cpuUtilEl.textContent = metrics.cpu_usage_percent?.toFixed(1) ?? 'N/A';
            ramUtilEl.textContent = metrics.memory?.percent?.toFixed(1) ?? 'N/A';
            gpuTempEl.textContent = metrics.gpu?.temperature_celsius?.toFixed(0) ?? 'N/A';
            
            if (metrics.locked) {
                busyStatusEl.textContent = '运行中';
                busyStatusEl.className = 'font-semibold busy-status text-blue-400';
            } else {
                busyStatusEl.textContent = '空闲';
                busyStatusEl.className = 'font-semibold busy-status text-green-400';
            }
        }
    } else {
        indicatorEl.classList.remove('bg-green-500');
        indicatorEl.classList.add('bg-red-500', 'animate-pulse');
        card.classList.remove('bg-gray-800', 'border-gray-700');
        card.classList.add('bg-gray-700', 'border-gray-600');
        
        gpuUtilEl.textContent = 'N/A';
        gpuMemEl.textContent = 'N/A';
        cpuUtilEl.textContent = 'N/A';
        ramUtilEl.textContent = 'N/A';
        gpuTempEl.textContent = 'N/A';
        busyStatusEl.textContent = '离线';
        busyStatusEl.className = 'font-semibold busy-status text-red-500';
    }
}

/**
 * Updates the main dashboard charts with new data from all nodes.
 * @param {Array} nodes - An array of node status objects.
 */
function updateDashboardCharts(nodes) {
    const onlineNodes = nodes.filter(n => n.online && n.metrics);
    const labels = onlineNodes.map(n => n.name);

    if (labels.length === 0) {
        // If no nodes are online, clear the charts
        cpuChart.data.labels = [];
        cpuChart.data.datasets[0].data = [];
        gpuChart.data.labels = [];
        gpuChart.data.datasets[0].data = [];
        memoryChart.data.labels = [];
        memoryChart.data.datasets[0].data = [];
        gpuMemoryChart.data.labels = [];
        gpuMemoryChart.data.datasets[0].data = [];
    } else {
        cpuChart.data.labels = labels;
        cpuChart.data.datasets[0].data = onlineNodes.map(n => n.metrics.cpu_usage_percent);

        gpuChart.data.labels = labels;
        gpuChart.data.datasets[0].data = onlineNodes.map(n => n.metrics.gpu.utilization_percent);

        memoryChart.data.labels = labels;
        memoryChart.data.datasets[0].data = onlineNodes.map(n => n.metrics.memory.percent);

        gpuMemoryChart.data.labels = labels;
        gpuMemoryChart.data.datasets[0].data = onlineNodes.map(n => n.metrics.gpu.memory_usage_percent);
    }

    cpuChart.update();
    gpuChart.update();
    memoryChart.update();
    gpuMemoryChart.update();
}

/**
 * Renders the list of active alerts.
 * @param {Array} alerts - An array of alert objects from the API.
 */
function updateAlerts(alerts) {
    if (!alertsContainer) return;
    alertsContainer.innerHTML = ''; // Clear previous alerts
    if (alerts.length === 0) {
        alertsContainer.innerHTML = '<p class="text-gray-400">当前无告警</p>';
        return;
    }

    alerts.forEach(alert => {
        const alertEl = document.createElement('div');
        alertEl.className = `p-3 rounded-lg mb-2 flex items-center ${alert.level === '严重' ? 'bg-red-900 border border-red-700' : 'bg-yellow-900 border border-yellow-700'}`;
        alertEl.innerHTML = `
            <span class="font-bold mr-2">[${alert.level}]</span>
            <span>${alert.message}</span>
        `;
        alertsContainer.appendChild(alertEl);
    });
}

/**
 * Populates the model selection dropdown with available models.
 * @param {Array} models - An array of model name strings.
 */
function updateModelSelector(models) {
    if (!modelSelect) return;
    const currentVal = modelSelect.value;
    modelSelect.innerHTML = '<option value="">默认</option>'; // Default option
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
    // Restore previous selection if it's still available
    if (models.includes(currentVal)) {
        modelSelect.value = currentVal;
    }
}

export {
    updateNodeCards,
    updateDashboardCharts,
    updateAlerts,
    updateModelSelector
};
