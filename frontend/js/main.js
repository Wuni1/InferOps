/**
 * InferOps - Main Frontend Application Logic
 *
 * This is the main entry point for the frontend JavaScript. It orchestrates the
 * different modules (API, UI, Chat, etc.) and sets up the main application loop
 * for periodically fetching and updating data.
 */

import { fetchNodeStatuses, fetchAlerts, fetchAvailableModels } from './api.js';
import { updateNodeCards, updateDashboardCharts, updateAlerts, updateModelSelector } from './ui.js';
import { initChat } from './chat.js';
import { initDatasetProcessing } from './dataset.js';

// The interval (in milliseconds) for polling the backend for status updates.
const UPDATE_INTERVAL = 2000; // 2 seconds

/**
 * The main application loop. Fetches all necessary data from the backend
 * and calls the UI functions to update the page.
 */
async function appTick() {
    try {
        // Fetch data in parallel for efficiency
        const [nodes, alerts, models] = await Promise.all([
            fetchNodeStatuses(),
            fetchAlerts(),
            fetchAvailableModels()
        ]);

        // Update UI components with the new data
        updateNodeCards(nodes);
        updateDashboardCharts(nodes);
        updateAlerts(alerts);
        updateModelSelector(models);

    } catch (error) {
        console.error("An error occurred in the main app loop:", error);
        // Here you could display a global error message to the user
    }
}

/**
 * Initializes the entire frontend application.
 */
function initialize() {
    // Set up event listeners for interactive components
    initChat();
    initDatasetProcessing();

    // Run the first data fetch immediately on load
    appTick();

    // Set up the periodic polling
    setInterval(appTick, UPDATE_INTERVAL);

    console.log("InferOps Frontend Initialized.");
}

// --- Application Start ---
// The `DOMContentLoaded` event ensures that the DOM is fully loaded before
// we try to manipulate it.
document.addEventListener('DOMContentLoaded', initialize);
