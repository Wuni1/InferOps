/**
 * InferOps - Charting Module
 *
 * This module initializes and configures all the charts used in the dashboard.
 * It uses Chart.js to create responsive and informative visualizations of node metrics.
 */

// Common configuration for all charts to maintain a consistent look and feel.
const commonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false,
        },
    },
    scales: {
        y: {
            beginAtZero: true,
            max: 100,
            ticks: {
                color: '#9CA3AF', // text-gray-400
            },
            grid: {
                color: '#374151', // bg-gray-700
            },
        },
        x: {
            ticks: {
                color: '#9CA3AF',
            },
            grid: {
                display: false,
            },
        },
    },
};

// --- Chart Initializations ---

// 1. CPU Utilization Chart
const cpuChartCtx = document.getElementById('cpu-chart')?.getContext('2d');
const cpuChart = cpuChartCtx ? new Chart(cpuChartCtx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'CPU 使用率',
            data: [],
            backgroundColor: 'rgba(59, 130, 246, 0.5)', // bg-blue-500
            borderColor: 'rgba(59, 130, 246, 1)',
            borderWidth: 1,
        }],
    },
    options: commonChartOptions,
}) : null;

// 2. GPU Utilization Chart
const gpuChartCtx = document.getElementById('gpu-chart')?.getContext('2d');
const gpuChart = gpuChartCtx ? new Chart(gpuChartCtx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'GPU 使用率',
            data: [],
            backgroundColor: 'rgba(16, 185, 129, 0.5)', // bg-green-500
            borderColor: 'rgba(16, 185, 129, 1)',
            borderWidth: 1,
        }],
    },
    options: commonChartOptions,
}) : null;

// 3. System Memory (RAM) Usage Chart
const memoryChartCtx = document.getElementById('memory-chart')?.getContext('2d');
const memoryChart = memoryChartCtx ? new Chart(memoryChartCtx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: '内存使用率',
            data: [],
            backgroundColor: 'rgba(234, 179, 8, 0.5)', // bg-yellow-500
            borderColor: 'rgba(234, 179, 8, 1)',
            borderWidth: 1,
        }],
    },
    options: commonChartOptions,
}) : null;

// 4. GPU Memory Usage Chart
const gpuMemoryChartCtx = document.getElementById('gpu-memory-chart')?.getContext('2d');
const gpuMemoryChart = gpuMemoryChartCtx ? new Chart(gpuMemoryChartCtx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'GPU 显存使用率',
            data: [],
            backgroundColor: 'rgba(139, 92, 246, 0.5)', // bg-violet-500
            borderColor: 'rgba(139, 92, 246, 1)',
            borderWidth: 1,
        }],
    },
    options: commonChartOptions,
}) : null;

export { cpuChart, gpuChart, memoryChart, gpuMemoryChart };
