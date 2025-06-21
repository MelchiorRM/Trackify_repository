// Posts JavaScript functionality

// Global variables
let currentPostId = null;
let shareModal = null;

// Get current user ID (set in HTML template)
let currentUserId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap modal
    shareModal = new bootstrap.Modal(document.getElementById('shareModal'));
    
    // Initialize comment inputs
    initializeCommentInputs();
    
    // Add event delegation for all post actions
    document.addEventListener('click', function(e) {
        const action = e.target.closest('[data-action]')?.dataset.action;
        const postId = e.target.closest('[data-post-id]')?.dataset.postId;
        const commentId = e.target.closest('[data-comment-id]')?.dataset.commentId;
        
        if (!action) return;
        
        switch (action) {
            case 'toggle-like':
                if (postId) toggleLike(parseInt(postId));
                break;
            case 'toggle-comments':
                if (postId) toggleComments(parseInt(postId));
                break;
            case 'repost':
                if (postId) repost(parseInt(postId));
                break;
            case 'share-to-message':
                if (postId) shareToMessage(parseInt(postId));
                break;
            case 'copy-link':
                if (postId) copyLink(parseInt(postId));
                break;
            case 'add-comment':
                if (postId) addComment(parseInt(postId));
                break;
            case 'delete-comment':
                if (commentId) deleteComment(parseInt(commentId));
                break;
            case 'delete-post':
                if (postId) deletePost(parseInt(postId));
                break;
        }
    });
});

// Like/Unlike functionality
async function toggleLike(postId) {
    try {
        const response = await fetch(`/api/post/${postId}/like`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const likeBtn = document.querySelector(`[data-post-id="${postId}"]`);
            const likeIcon = likeBtn.querySelector('i');
            const likeCount = likeBtn.querySelector('.like-count');
            
            // Update like count
            likeCount.textContent = data.like_count;
            
            // Update icon appearance
            if (data.action === 'liked') {
                likeIcon.classList.add('text-danger');
                showToast('Post liked!', 'success');
            } else {
                likeIcon.classList.remove('text-danger');
                showToast('Post unliked', 'info');
            }
        } else {
            showToast('Error updating like', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error', 'error');
    }
}

// Toggle comments section
function toggleComments(postId) {
    const commentsSection = document.getElementById(`comments-${postId}`);
    const isVisible = commentsSection.style.display !== 'none';
    
    if (isVisible) {
        commentsSection.style.display = 'none';
    } else {
        commentsSection.style.display = 'block';
        // Focus on comment input
        const commentInput = commentsSection.querySelector('.comment-input');
        if (commentInput) {
            commentInput.focus();
        }
    }
}

// Add comment functionality
async function addComment(postId) {
    const commentInput = document.querySelector(`[data-post-id="${postId}"].comment-input`);
    const content = commentInput.value.trim();
    
    if (!content) {
        showToast('Please enter a comment', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/post/${postId}/comment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: content })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Add comment to DOM
            addCommentToDOM(postId, data.comment);
            
            // Clear input
            commentInput.value = '';
            
            // Update comment count
            updateCommentCount(postId, 1);
            
            showToast('Comment added!', 'success');
        } else {
            showToast(data.error || 'Error adding comment', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error', 'error');
    }
}

// Add comment to DOM
function addCommentToDOM(postId, comment) {
    const commentsList = document.querySelector(`#comments-${postId} .comments-list`);
    const commentHTML = `
        <div class="comment-item mb-2" data-comment-id="${comment.id}">
            <div class="d-flex align-items-start">
                <img src="${comment.user.profile_picture || '/static/defaults/user.png'}" 
                     class="rounded-circle me-2" style="width: 30px; height: 30px; object-fit: cover;">
                <div class="flex-grow-1">
                    <div class="comment-content">
                        <strong>${comment.user.username}</strong>
                        <span class="comment-text">${comment.content}</span>
                    </div>
                    <small class="text-muted">${comment.created_at}</small>
                </div>
                <button class="btn btn-sm btn-outline-danger ms-2" 
                        onclick="deleteComment(${comment.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    commentsList.insertAdjacentHTML('afterbegin', commentHTML);
}

// Delete comment
async function deleteComment(commentId) {
    if (!confirm('Are you sure you want to delete this comment?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/post/${commentId}/comment/${commentId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Remove comment from DOM
            const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
            if (commentElement) {
                commentElement.remove();
                
                // Update comment count
                const postId = commentElement.closest('.post-card').dataset.postId;
                updateCommentCount(postId, -1);
            }
            
            showToast('Comment deleted', 'success');
        } else {
            showToast(data.error || 'Error deleting comment', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error', 'error');
    }
}

// Update comment count
function updateCommentCount(postId, change) {
    const commentBtn = document.querySelector(`[data-post-id="${postId}"]`).parentNode.querySelector('.comment-count');
    const currentCount = parseInt(commentBtn.textContent);
    commentBtn.textContent = currentCount + change;
}

// Repost functionality
async function repost(postId) {
    if (!confirm('Are you sure you want to repost this?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/post/${postId}/repost`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Post reposted successfully!', 'success');
            // Optionally redirect to posts page to see the repost
            setTimeout(() => {
                window.location.href = '/posts';
            }, 1000);
        } else {
            showToast(data.error || 'Error reposting', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error', 'error');
    }
}

// Share to message functionality
async function shareToMessage(postId) {
    currentPostId = postId;
    
    try {
        // Load users for dropdown
        const response = await fetch('/api/users');
        const users = await response.json();
        
        const select = document.getElementById('recipientSelect');
        select.innerHTML = '<option value="">Choose a user...</option>';
        
        users.forEach(user => {
            if (user.user_id != currentUserId) { // Don't show current user
                const option = document.createElement('option');
                option.value = user.user_id;
                option.textContent = user.username;
                select.appendChild(option);
            }
        });
        
        shareModal.show();
    } catch (error) {
        console.error('Error loading users:', error);
        showToast('Error loading users', 'error');
    }
}

// Send shared post
async function sendSharedPost() {
    const recipientId = document.getElementById('recipientSelect').value;
    
    if (!recipientId) {
        showToast('Please select a recipient', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/post/${currentPostId}/share`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ recipient_id: recipientId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            shareModal.hide();
            showToast('Post shared successfully!', 'success');
        } else {
            showToast(data.error || 'Error sharing post', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error', 'error');
    }
}

// Copy link functionality
function copyLink(postId) {
    const url = `${window.location.origin}/post/${postId}`;
    
    navigator.clipboard.writeText(url).then(() => {
        showToast('Link copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Link copied to clipboard!', 'success');
    });
}

// Delete post functionality
async function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/post/${postId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            // Remove post from DOM
            const postElement = document.querySelector(`[data-post-id="${postId}"]`);
            if (postElement) {
                postElement.remove();
            }
            showToast('Post deleted successfully!', 'success');
        } else {
            showToast('Error deleting post', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error', 'error');
    }
}

// Initialize comment inputs
function initializeCommentInputs() {
    document.querySelectorAll('.comment-input').forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const postId = this.dataset.postId;
                addComment(postId);
            }
        });
    });
}

// Toast notification system
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        `;
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
} 