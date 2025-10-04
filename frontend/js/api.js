/**
 * InferOps - API Interaction Module
 *
 * This module centralizes all communication with the backend gateway API.
 * By abstracting API calls into dedicated functions, we can easily manage
 * endpoints, handle errors, and mock data for testing.
 */

const API_BASE_URL = "/api/v1";

/**
 * Fetches the status of all compute nodes from the gateway.
 * @returns {Promise<Array>} A promise that resolves to an array of node status objects.
 */
async function fetchNodeStatuses() {
    try {
        const response = await fetch(`${API_BASE_URL}/status/all`);
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch node statuses:", error);
        return []; // Return an empty array on failure to prevent crashes
    }
}

/**
 * Fetches the list of currently active system alerts.
 * @returns {Promise<Array>} A promise that resolves to an array of alert objects.
 */
async function fetchAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/alerts`);
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch alerts:", error);
        return [];
    }
}

/**
 * Fetches the list of unique models available across all online nodes.
 * @returns {Promise<Array>} A promise that resolves to an array of model name strings.
 */
async function fetchAvailableModels() {
    try {
        const response = await fetch(`${API_BASE_URL}/models`);
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch models:", error);
        return [];
    }
}

/**
 * Uploads a dataset file for batch processing.
 * @param {FormData} formData - The form data containing the file and other options.
 * @returns {Promise<Object>} A promise that resolves to the job creation response.
 */
async function uploadDataset(formData) {
    const response = await fetch(`${API_BASE_URL}/dataset/upload`, {
        method: 'POST',
        body: formData,
    });
    return await response.json();
}

/**
 * Fetches the status of a specific dataset processing job.
 * @param {string} jobId - The ID of the job to check.
 * @returns {Promise<Object>} A promise that resolves to the job status object.
 */
async function fetchJobStatus(jobId) {
    const response = await fetch(`${API_BASE_URL}/dataset/status/${jobId}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch status for job ${jobId}`);
    }
    return await response.json();
}

export { 
    fetchNodeStatuses, 
    fetchAlerts, 
    fetchAvailableModels,
    uploadDataset,
    fetchJobStatus
};
