// Conversation JavaScript functionality

let messageInput = null;
let sendBtn = null;
let messagesArea = null;
let isTyping = false;
let typingTimeout = null;
let containerEl = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeConversation();
});

function initializeConversation() {
    containerEl = document.querySelector('.conversation-container');
    messageInput = document.getElementById('messageInput');
    sendBtn = document.getElementById('sendBtn');
    messagesArea = document.getElementById('messagesArea');
    
    if (!messageInput || !sendBtn || !messagesArea) return;
    
    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        autoResizeTextarea(this);
        handleTyping();
    });
    
    // Send message on Enter (but allow Shift+Enter for new line)
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Focus on input
    messageInput.focus();
    
    // Scroll to bottom
    scrollToBottom();
    
    // Ensure click handler is bound even if inline onclick fails
    try {
        sendBtn.removeEventListener('click', sendMessage);
    } catch (e) {}
    sendBtn.addEventListener('click', function(e) {
        e.preventDefault();
        sendMessage();
    });

    // Start real-time updates
    startRealTimeUpdates();
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function handleTyping() {
    if (!isTyping) {
        isTyping = true;
        // Could send typing indicator to server here
    }
    
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        isTyping = false;
        // Could send stop typing indicator to server here
    }, 1000);
}

function sendMessage() {
    const content = messageInput.value.trim();
    if (!content) return;
    
    // Disable send button
    sendBtn.disabled = true;
    
    const otherUserIdLocal = parseInt(messagesArea?.dataset.otherUserId || containerEl?.dataset.otherUserId || window.otherUserId || 0);
    if (!otherUserIdLocal || Number.isNaN(otherUserIdLocal)) {
        console.error('Missing otherUserId for conversation');
        showToast('Cannot determine recipient. Please re-open the conversation.', 'error');
        sendBtn.disabled = false;
        return;
    }
    fetch(`/messages/${otherUserIdLocal}/send`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    })
    .then(async response => {
        if (!response.ok) {
            const text = await response.text();
            throw new Error(text || `HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Add message to display
            addMessageToDisplay(data.message, true);
            
            // Clear input
            messageInput.value = '';
            messageInput.style.height = 'auto';
            
            // Scroll to bottom
            scrollToBottom();
        } else {
            showToast(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error sending message:', error);
        showToast('Error sending message', 'error');
    })
    .finally(() => {
        sendBtn.disabled = false;
        messageInput.focus();
    });
}

function addMessageToDisplay(message, isSent = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isSent ? 'sent' : 'received'} fade-in`;
    messageDiv.dataset.messageId = message.id;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = message.content;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = message.created_at;
    
    if (isSent) {
        const checkIcon = document.createElement('i');
        checkIcon.className = 'fas fa-check-double ms-1';
        time.appendChild(checkIcon);
    }
    
    bubble.appendChild(content);
    bubble.appendChild(time);
    messageDiv.appendChild(bubble);
    
    messagesArea.appendChild(messageDiv);
}

function scrollToBottom() {
    if (messagesArea) {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
}

function startRealTimeUpdates() {
    // Poll for new messages every 3 seconds
    setInterval(() => {
        fetchNewMessages();
    }, 3000);
}

function fetchNewMessages() {
    const otherUserIdLocal = parseInt(messagesArea?.dataset.otherUserId || containerEl?.dataset.otherUserId || window.otherUserId || 0);
    fetch(`/api/messages/${otherUserIdLocal}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateMessages(data.messages);
            }
        })
        .catch(error => {
            console.error('Error fetching messages:', error);
        });
}

function updateMessages(messages) {
    const currentMessageIds = Array.from(messagesArea.children).map(el => el.dataset.messageId);
    const newMessages = messages.filter(msg => !currentMessageIds.includes(msg.id.toString()));
    
    newMessages.forEach(message => {
        const isSent = message.sender_id === currentUserId;
        addMessageToDisplay(message, isSent);
    });
    
    if (newMessages.length > 0) {
        scrollToBottom();
        updateMessageStatus(newMessages);
    }
}

function updateMessageStatus(messages) {
    messages.forEach(message => {
        if (message.sender_id === currentUserId) {
            const messageElement = messagesArea.querySelector(`[data-message-id="${message.id}"]`);
            if (messageElement) {
                const checkIcon = messageElement.querySelector('.fa-check-double');
                if (checkIcon && message.is_read) {
                    checkIcon.classList.add('text-primary');
                }
            }
        }
    });
}

function shareMedia() {
    const modal = new bootstrap.Modal(document.getElementById('shareMediaModal'));
    modal.show();
    
    // Initialize media search
    const searchInput = document.getElementById('mediaSearch');
    const mediaType = document.getElementById('mediaType');
    
    function performMediaSearch() {
        const query = searchInput.value.trim();
        const type = mediaType.value;
        
        if (!query) {
            document.getElementById('mediaSearchResults').innerHTML = '';
            return;
        }
        
        // This would call your media search API
        // For now, we'll show a placeholder
        document.getElementById('mediaSearchResults').innerHTML = `
            <div class="col-12">
                <p class="text-muted text-center">Search functionality would be implemented here</p>
            </div>
        `;
    }
    
    searchInput.addEventListener('input', performMediaSearch);
    mediaType.addEventListener('change', performMediaSearch);
}

function showUserProfile() {
    // Navigate to user profile
    window.open(`/profile/${otherUsername}`, '_blank');
}

function clearConversation() {
    if (confirm('Are you sure you want to clear this conversation? This action cannot be undone.')) {
        // This would call an API to clear the conversation
        showToast('Conversation cleared', 'success');
    }
}

// Toast notification system
function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <span>${message}</span>
            <button type="button" class="btn-close btn-close-sm" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
}

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, could pause real-time updates
    } else {
        // Page is visible, refresh messages
        fetchNewMessages();
    }
});

// Handle window focus
window.addEventListener('focus', function() {
    fetchNewMessages();
}); 