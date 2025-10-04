/**
 * InferOps - Dataset Processing Module
 *
 * This module handles the UI and logic for the dataset processing feature.
 * It allows users to upload a dataset, start a batch processing job, and
 * monitor its progress in real-time.
 */

import { uploadDataset, fetchJobStatus } from './api.js';

// DOM Elements
const datasetForm = document.getElementById('dataset-form');
const fileInput = document.getElementById('dataset-file');
const dataCountInput = document.getElementById('data-count');
const jobStatusContainer = document.getElementById('job-status-container');
const jobProgress = document.getElementById('job-progress');
const jobProgressText = document.getElementById('job-progress-text');
const jobResultsContainer = document.getElementById('job-results');

// State
let currentJobId = null;
let jobStatusInterval = null;

/**
 * Initializes the dataset processing form and related event listeners.
 */
function initDatasetProcessing() {
    if (datasetForm) {
        datasetForm.addEventListener('submit', handleFormSubmit);
    }
}

/**
 * Handles the submission of the dataset upload form.
 * @param {Event} e - The form submission event.
 */
async function handleFormSubmit(e) {
    e.preventDefault();
    if (!fileInput.files.length) {
        alert('请选择一个数据集文件 (JSON).');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (dataCountInput.value) {
        formData.append('data_count', dataCountInput.value);
    }

    try {
        const response = await uploadDataset(formData);
        if (response.job_id) {
            currentJobId = response.job_id;
            jobStatusContainer.classList.remove('hidden');
            jobResultsContainer.innerHTML = ''; // Clear previous results
            startJobMonitoring();
        } else {
            throw new Error(response.detail || 'Failed to start job.');
        }
    } catch (error) {
        console.error('Error uploading dataset:', error);
        alert(`Error: ${error.message}`);
    }
}

/**
 * Starts periodically polling for the status of the current job.
 */
function startJobMonitoring() {
    if (jobStatusInterval) {
        clearInterval(jobStatusInterval);
    }
    // Poll for status every 2 seconds
    jobStatusInterval = setInterval(updateJobStatus, 2000);
}

/**
 * Fetches and updates the UI with the latest job status.
 */
async function updateJobStatus() {
    if (!currentJobId) return;

    try {
        const status = await fetchJobStatus(currentJobId);
        const progressPercent = status.total_items > 0 
            ? (status.processed_items / status.total_items) * 100 
            : 0;

        jobProgress.style.width = `${progressPercent}%`;
        jobProgressText.textContent = `处理中: ${status.processed_items} / ${status.total_items} (${status.status})`;

        // Render new results incrementally
        renderJobResults(status.results);

        if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(jobStatusInterval);
            jobStatusInterval = null;
            jobProgressText.textContent = `任务完成: ${status.processed_items} / ${status.total_items} (${status.status})`;
        }
    } catch (error) {
        console.error('Failed to update job status:', error);
        clearInterval(jobStatusInterval);
        jobStatusInterval = null;
        jobProgressText.textContent = '错误: 无法获取任务状态';
    }
}

/**
 * Renders the results of the dataset processing job.
 * This function is designed to be incremental, only adding new results.
 * @param {Array} results - The array of result objects from the job status.
 */
function renderJobResults(results) {
    // Get the number of currently rendered results
    const renderedCount = jobResultsContainer.children.length;

    // Only append new results
    for (let i = renderedCount; i < results.length; i++) {
        const result = results[i];
        const resultEl = document.createElement('div');
        resultEl.className = 'p-3 bg-gray-700 rounded-md text-sm';
        resultEl.innerHTML = `
            <p><span class="font-semibold text-gray-400">输入:</span> ${JSON.stringify(result.original)}</p>
            <p><span class="font-semibold text-green-400">输出:</span> ${JSON.stringify(result.output)}</p>
        `;
        jobResultsContainer.appendChild(resultEl);
    }
    // Auto-scroll to the bottom
    jobResultsContainer.scrollTop = jobResultsContainer.scrollHeight;
}

export { initDatasetProcessing };
