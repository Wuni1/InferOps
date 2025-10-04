/**
 * InferOps - Chat Interaction Module
 *
 * This module handles the logic for the real-time chat interface. It manages
 * sending user messages, receiving streamed responses from the LLM, and
 * rendering the conversation history.
 */

// DOM Elements
const chatWindow = document.getElementById('chat-window');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const modelSelect = document.getElementById('model-select');

// State for the current conversation
let conversationHistory = [];

/**
 * Initializes chat functionality by adding event listeners.
 */
function initChat() {
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    if (messageInput) {
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
}

/**
 * Sends the user's message to the backend and handles the streamed response.
 */
async function sendMessage() {
    const messageText = messageInput.value.trim();
    if (!messageText) return;

    // Add user message to history and render it
    const userMessage = { role: 'user', content: messageText };
    conversationHistory.push(userMessage);
    renderMessage(userMessage);

    // Clear input and disable send button
    messageInput.value = '';
    sendButton.disabled = true;

    // Create a placeholder for the assistant's response
    const assistantMessage = { role: 'assistant', content: '' };
    const assistantMessageElement = renderMessage(assistantMessage, true); // Render with streaming flag
    const contentElement = assistantMessageElement.querySelector('.message-content');

    try {
        const response = await fetch('/api/v1/chat/completions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: conversationHistory,
                model: modelSelect.value || null,
                stream: true,
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        // Listen for the custom 'node_assigned' event
        const eventSource = new EventSource('/api/v1/chat/completions'); // This is a slight hack to reuse the connection for events
        
        // This part is tricky to implement correctly without a full EventSource client.
        // The main fetch handles the data stream, but we can't easily get custom events.
        // The backend sends a special event at the start, which we'll simulate handling.
        // A more robust solution would use a library that properly handles Server-Sent Events.

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep the last, possibly incomplete, line

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.substring(6);
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.choices && parsed.choices[0].delta.content) {
                            assistantMessage.content += parsed.choices[0].delta.content;
                            // Use marked.js to render markdown in real-time
                            contentElement.innerHTML = marked.parse(assistantMessage.content);
                            chatWindow.scrollTop = chatWindow.scrollHeight;
                        }
                    } catch (e) {
                        // Handle non-JSON data, like the initial [DONE] from some servers
                    }
                } else if (line.startsWith('event: node_assigned')) {
                    // This is a simplified way to handle the custom event.
                    // A proper SSE client would handle this more cleanly.
                    const nextLine = lines[lines.indexOf(line) + 1];
                    if (nextLine && nextLine.startsWith('data: ')) {
                        const data = nextLine.substring(6);
                        const parsed = JSON.parse(data);
                        displayNodeAssignment(parsed.node_name);
                    }
                }
            }
        }
        
        // Final parse after stream is complete
        contentElement.innerHTML = marked.parse(assistantMessage.content);

    } catch (error) {
        console.error('Error during chat:', error);
        contentElement.innerHTML = `<p class="text-red-400">Error: Could not connect to the InferOps gateway.</p>`;
    } finally {
        // Re-enable send button and add the final assistant message to history
        sendButton.disabled = false;
        conversationHistory.push(assistantMessage);
        assistantMessageElement.classList.remove('streaming');
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

/**
 * Renders a single message in the chat window.
 * @param {Object} message - The message object { role, content }.
 * @param {boolean} isStreaming - Whether the message is currently being streamed.
 * @returns {HTMLElement} The created message element.
 */
function renderMessage(message, isStreaming = false) {
    const messageElement = document.createElement('div');
    const isUser = message.role === 'user';
    
    messageElement.className = `p-4 my-2 rounded-lg max-w-3xl w-fit ${isUser ? 'bg-blue-900 self-end' : 'bg-gray-700 self-start'}`;
    if (isStreaming) {
        messageElement.classList.add('streaming');
    }

    // Use marked.js to parse Markdown content
    const contentHTML = marked.parse(message.content || "...");
    
    messageElement.innerHTML = `
        <div class="font-bold text-sm mb-1">${isUser ? 'You' : 'InferOps Assistant'}</div>
        <div class="message-content prose prose-invert max-w-none">${contentHTML}</div>
    `;
    
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return messageElement;
}

/**
 * Displays a temporary notification about which node is handling the request.
 * @param {string} nodeName - The name of the assigned node.
 */
function displayNodeAssignment(nodeName) {
    const notification = document.createElement('div');
    notification.className = 'text-center text-xs text-gray-400 my-2 p-1 bg-gray-800 rounded-full w-fit mx-auto px-3';
    notification.textContent = `任务已分配至 ${nodeName}`;
    
    chatWindow.appendChild(notification);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Remove the notification after a few seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

export { initChat };
