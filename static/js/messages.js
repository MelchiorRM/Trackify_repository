// Messages JavaScript functionality

let currentConversation = null;
let searchTimeout = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeMessages();
});

function initializeMessages() {
    // Initialize search functionality
    const searchInput = document.getElementById('searchConversations');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                searchConversations(this.value);
            }, 300);
        });
    }

    // Add event delegation for conversation items
    document.addEventListener('click', function(e) {
        const conversationItem = e.target.closest('.conversation-item');
        if (conversationItem) {
            const userId = conversationItem.dataset.userId;
            if (userId) {
                loadConversation(parseInt(userId));
            }
        }
    });

    // Auto-refresh unread count
    setInterval(updateUnreadCount, 30000); // Every 30 seconds
}

function searchConversations(query) {
    const conversationItems = document.querySelectorAll('.conversation-item');
    
    conversationItems.forEach(item => {
        const username = item.querySelector('.conversation-name').textContent.toLowerCase();
        const preview = item.querySelector('.conversation-preview').textContent.toLowerCase();
        
        if (username.includes(query.toLowerCase()) || preview.includes(query.toLowerCase())) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function loadConversation(userId) {
    // Update active conversation
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const selectedItem = document.querySelector(`[data-user-id="${userId}"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
        selectedItem.classList.remove('unread');
        selectedItem.querySelector('.unread-badge')?.remove();
    }
    
    // Load conversation in the right panel
    fetch(`/messages/${userId}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('conversationArea').innerHTML = html;
            currentConversation = userId;
            
            // Initialize conversation functionality
            initializeConversation();
        })
        .catch(error => {
            console.error('Error loading conversation:', error);
            showToast('Error loading conversation', 'error');
        });
}

function showNewMessageModal() {
    const modal = new bootstrap.Modal(document.getElementById('newMessageModal'));
    modal.show();
    
    // Initialize user search
    const searchInput = document.getElementById('userSearch');
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchUsers(this.value);
        }, 300);
    });
}

function searchUsers(query) {
    if (!query.trim()) {
        document.getElementById('userSearchResults').innerHTML = '';
        return;
    }
    
    fetch(`/api/messages/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayUserSearchResults(data.users);
            } else {
                showToast(data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error searching users:', error);
            showToast('Error searching users', 'error');
        });
}

function displayUserSearchResults(users) {
    const resultsContainer = document.getElementById('userSearchResults');
    
    if (users.length === 0) {
        resultsContainer.innerHTML = '<p class="text-muted text-center p-3">No users found</p>';
        return;
    }
    
    const html = users.map(user => `
        <div class="list-group-item list-group-item-action d-flex align-items-center" 
             onclick="startConversation(${user.user_id})">
            <img src="${user.profile_picture || '/static/defaults/user.png'}" 
                 class="rounded-circle me-3" style="width: 40px; height: 40px; object-fit: cover;">
            <div>
                <h6 class="mb-0">${user.username}</h6>
            </div>
        </div>
    `).join('');
    
    resultsContainer.innerHTML = html;
}

function startConversation(userId) {
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('newMessageModal'));
    modal.hide();
    
    // Load conversation
    loadConversation(userId);
}

function updateUnreadCount() {
    fetch('/api/messages/unread')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateUnreadBadge(data.unread_count);
            }
        })
        .catch(error => {
            console.error('Error updating unread count:', error);
        });
}

function updateUnreadBadge(count) {
    // Update navigation badge if it exists
    const navBadge = document.querySelector('.nav-link[href="/messages"] .badge');
    if (navBadge) {
        if (count > 0) {
            navBadge.textContent = count;
            navBadge.style.display = 'inline';
        } else {
            navBadge.style.display = 'none';
        }
    }
}

function initializeConversation() {
    // This will be called when a conversation is loaded
    // The actual conversation functionality is in conversation.js
}

// Real-time updates (if WebSocket is implemented)
function setupRealTimeUpdates() {
    // This would connect to WebSocket for real-time message updates
    // For now, we'll use polling
    setInterval(() => {
        if (currentConversation) {
            refreshConversation();
        }
    }, 5000); // Every 5 seconds
}

function refreshConversation() {
    if (!currentConversation) return;
    
    fetch(`/api/messages/${currentConversation}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateMessagesDisplay(data.messages);
            }
        })
        .catch(error => {
            console.error('Error refreshing conversation:', error);
        });
}

function updateMessagesDisplay(messages) {
    const messagesArea = document.getElementById('messagesArea');
    if (!messagesArea) return;
    
    // Update messages (this would be more sophisticated in a real implementation)
    // For now, just scroll to bottom if new messages exist
    const currentMessageCount = messagesArea.children.length;
    if (messages.length > currentMessageCount) {
        scrollToBottom();
    }
}

function scrollToBottom() {
    const messagesArea = document.getElementById('messagesArea');
    if (messagesArea) {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
}

// Toast notification system
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <span>${message}</span>
            <button type="button" class="btn-close btn-close-sm" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
}

// Initialize real-time updates
setupRealTimeUpdates(); 