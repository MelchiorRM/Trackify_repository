// Custom JavaScript for enhanced UI/UX

// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    for (const link of links) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
});

// Simple form validation example
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let valid = true;
            const inputs = form.querySelectorAll('input[required], textarea[required]');
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.style.borderColor = 'red';
                } else {
                    input.style.borderColor = '';
                }
            });
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
});

// Network Page Functions
document.addEventListener('DOMContentLoaded', function() {
    // Network page tab switching
    const followersTab = document.getElementById('followersTab');
    const followingTab = document.getElementById('followingTab');
    const followersSection = document.getElementById('followersSection');
    const followingSection = document.getElementById('followingSection');

    if (followersTab && followingTab) {
        followersTab.addEventListener('click', function() {
            followersTab.classList.add('active');
            followingTab.classList.remove('active');
            followersSection.classList.remove('d-none');
            followingSection.classList.add('d-none');
        });

        followingTab.addEventListener('click', function() {
            followingTab.classList.add('active');
            followersTab.classList.remove('active');
            followingSection.classList.remove('d-none');
            followersSection.classList.add('d-none');
        });
    }

    // Profile picture preview
    const profilePictureInput = document.getElementById('profile_picture');
    const profilePicturePreview = document.querySelector('.profile-picture-preview');

    if (profilePictureInput && profilePicturePreview) {
        profilePictureInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePicturePreview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }
});

// Planner Page Functions
function addMedia() {
    const form = document.getElementById('addMediaForm');
    const formData = new FormData(form);
    const data = {
        media_type: formData.get('media_type'),
        title: formData.get('title'),
        planned_date: formData.get('planned_date'),
        notes: formData.get('notes')
    };

    fetch('/api/media/plan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', 'Media added to planner successfully!');
            bootstrap.Modal.getInstance(document.getElementById('addMediaModal')).hide();
            location.reload();
        } else {
            showAlert('error', data.error || 'Failed to add media to planner');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Failed to add media to planner');
    });
}

function markAsCompleted(mediaId) {
    fetch(`/api/media/${mediaId}/complete`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', 'Media marked as completed!');
            location.reload();
        } else {
            showAlert('error', 'Failed to mark media as completed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Failed to mark media as completed');
    });
}

function removeFromPlanner(mediaId) {
    if (!confirm('Are you sure you want to remove this media from your planner?')) {
        return;
    }

    fetch(`/api/media/${mediaId}/remove`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', 'Media removed from planner!');
            location.reload();
        } else {
            showAlert('error', 'Failed to remove media from planner');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Failed to remove media from planner');
    });
}

function updateMediaDate(event) {
    fetch(`/api/media/${event.extendedProps.mediaId}/update-date`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            planned_date: event.start.toISOString().split('T')[0]
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', 'Date updated successfully!');
        } else {
            showAlert('error', 'Failed to update date');
            calendar.refetchEvents();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Failed to update date');
        calendar.refetchEvents();
    });
}

function createList() {
    const form = document.getElementById('createListForm');
    const formData = new FormData(form);

    fetch('/api/lists/create', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showAlert('Error creating list', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('An error occurred', 'danger');
    });
}

// Stats Page Functions
function initializeCharts() {
    // Book Genres Chart
    const bookGenresCtx = document.getElementById('bookGenresChart');
    if (bookGenresCtx) {
        new Chart(bookGenresCtx, {
            type: 'pie',
            data: {
                labels: bookGenresLabels,
                datasets: [{
                    data: bookGenresData,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ]
                }]
            }
        });
    }

    // Movie Genres Chart
    const movieGenresCtx = document.getElementById('movieGenresChart');
    if (movieGenresCtx) {
        new Chart(movieGenresCtx, {
            type: 'pie',
            data: {
                labels: movieGenresLabels,
                datasets: [{
                    data: movieGenresData,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ]
                }]
            }
        });
    }

    // Monthly Activity Chart
    const monthlyActivityCtx = document.getElementById('monthlyActivityChart');
    if (monthlyActivityCtx) {
        new Chart(monthlyActivityCtx, {
            type: 'line',
            data: {
                labels: monthlyActivityLabels,
                datasets: [{
                    label: 'Books',
                    data: monthlyActivityBooks,
                    borderColor: '#FF6384',
                    fill: false
                }, {
                    label: 'Movies',
                    data: monthlyActivityMovies,
                    borderColor: '#36A2EB',
                    fill: false
                }, {
                    label: 'Music',
                    data: monthlyActivityMusic,
                    borderColor: '#FFCE56',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Utility Functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Initialize charts when the page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('bookGenresChart')) {
        initializeCharts();
    }
});
