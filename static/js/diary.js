// Diary System JavaScript
class DiaryManager {
    constructor() {
        this.currentPage = 1;
        this.currentFilters = {
            search: '',
            mood: '',
            type: '',
            sort: 'date_desc'
        };
        this.currentEntry = null;
        this.entryModal = null;
        this.detailModal = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadMoods();
        this.loadStats();
        this.loadEntries();
        this.loadLibrary();
        this.initializeModals();
        this.handleUrlParameters();
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.currentFilters.search = searchInput.value;
                this.currentPage = 1;
                this.loadEntries();
            }, 300));
        }

        // Filter controls
        const moodFilter = document.getElementById('moodFilter');
        if (moodFilter) {
            moodFilter.addEventListener('change', () => {
                this.currentFilters.mood = moodFilter.value;
                this.currentPage = 1;
                this.loadEntries();
            });
        }

        const typeFilter = document.getElementById('typeFilter');
        if (typeFilter) {
            typeFilter.addEventListener('change', () => {
                this.currentFilters.type = typeFilter.value;
                this.currentPage = 1;
                this.loadEntries();
            });
        }

        const sortFilter = document.getElementById('sortFilter');
        if (sortFilter) {
            sortFilter.addEventListener('change', () => {
                this.currentFilters.sort = sortFilter.value;
                this.currentPage = 1;
                this.loadEntries();
            });
        }
    }

    async loadLibrary() {
        try {
            const response = await fetch('/api/library');
            const data = await response.json();
            if (data.success) {
                const select = document.getElementById('entryMedia');
                if (!select) return;
                // Clear except first
                while (select.children.length > 1) select.removeChild(select.lastChild);
                data.items.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.user_media_id;
                    option.textContent = `${this.capitalizeFirst(item.media_type)}: ${item.title}`;
                    select.appendChild(option);
                });
            }
        } catch (e) {
            console.error('Failed to load library', e);
        }
    }

    initializeModals() {
        this.entryModal = new bootstrap.Modal(document.getElementById('entryModal'));
        this.detailModal = new bootstrap.Modal(document.getElementById('entryDetailModal'));
    }

    async loadMoods() {
        try {
            const response = await fetch('/api/diary/moods');
            const data = await response.json();
            
            if (data.success) {
                this.populateMoodOptions(data.moods);
            }
        } catch (error) {
            console.error('Error loading moods:', error);
        }
    }

    populateMoodOptions(moods) {
        const moodSelects = [
            document.getElementById('entryMood'),
            document.getElementById('moodFilter')
        ];

        moodSelects.forEach(select => {
            if (select) {
                // Clear existing options except the first one
                while (select.children.length > 1) {
                    select.removeChild(select.lastChild);
                }

                // Add mood options
                moods.forEach(mood => {
                    const option = document.createElement('option');
                    option.value = mood;
                    option.textContent = this.capitalizeFirst(mood);
                    select.appendChild(option);
                });
            }
        });
    }

    async loadStats() {
        try {
            const response = await fetch('/api/diary/stats');
            const data = await response.json();
            
            if (data.success) {
                this.updateStats(data.stats);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    updateStats(stats) {
        document.getElementById('totalEntries').textContent = stats.total_entries;
        
        // Calculate this month's entries
        const currentMonth = new Date().toISOString().slice(0, 7);
        const thisMonthCount = stats.monthly_stats.find(s => s.month === currentMonth)?.count || 0;
        document.getElementById('thisMonth').textContent = thisMonthCount;
        
        document.getElementById('totalTags').textContent = stats.top_tags.length;
        
        // Get top mood
        const topMood = stats.mood_stats.length > 0 ? stats.mood_stats[0].mood : '-';
        document.getElementById('topMood').textContent = this.capitalizeFirst(topMood);
    }

    async loadEntries() {
        this.showLoading(true);
        
        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: 12,
                ...this.currentFilters
            });

            const response = await fetch(`/api/diary?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderEntries(data.entries);
                this.renderPagination(data.pagination);
            } else {
                this.showError('Failed to load entries');
            }
        } catch (error) {
            console.error('Error loading entries:', error);
            this.showError('Error loading entries');
        } finally {
            this.showLoading(false);
        }
    }

    renderEntries(entries) {
        const grid = document.getElementById('entriesGrid');
        const emptyState = document.getElementById('emptyState');
        
        if (entries.length === 0) {
            grid.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }
        
        emptyState.style.display = 'none';
        
        grid.innerHTML = entries.map(entry => this.createEntryCard(entry)).join('');
        
        // Add click listeners to cards
        grid.querySelectorAll('.entry-card').forEach((card, index) => {
            card.addEventListener('click', () => {
                this.showEntryDetail(entries[index]);
            });
        });
    }

    createEntryCard(entry) {
        const date = new Date(entry.created_at).toLocaleDateString();
        const moodClass = entry.mood ? `mood-${entry.mood}` : 'mood-neutral';
        const moodIcon = this.getMoodIcon(entry.mood);
        const tags = entry.tags.map(tag => `<span class="entry-tag">${tag}</span>`).join('');
        const mediaSection = entry.media ? this.createMediaSection(entry.media) : '';
        const privateBadge = entry.is_private ? '<span class="entry-private">Private</span>' : '';
        
        return `
            <div class="entry-card" data-entry-id="${entry.entry_id}">
                <div class="entry-header">
                    <div class="entry-title">${entry.title || 'Untitled Entry'}</div>
                    <div class="entry-meta">
                        <div class="entry-mood">
                            <div class="mood-icon ${moodClass}">${moodIcon}</div>
                            ${entry.mood ? this.capitalizeFirst(entry.mood) : 'No mood'}
                        </div>
                        <div class="entry-date">${date}</div>
                        ${privateBadge}
                    </div>
                </div>
                <div class="entry-body">
                    <div class="entry-content">${this.truncateText(entry.content, 150)}</div>
                    ${tags ? `<div class="entry-tags">${tags}</div>` : ''}
                    ${mediaSection}
                </div>
                <div class="entry-actions">
                    <div class="action-buttons">
                        <button class="action-btn edit" onclick="event.stopPropagation(); diaryManager.editEntry(${entry.entry_id})">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="action-btn delete" onclick="event.stopPropagation(); diaryManager.deleteEntry(${entry.entry_id})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    createMediaSection(media) {
        return `
            <div class="entry-media">
                <div class="media-title">${media.title}</div>
                <div class="media-info">
                    ${media.media_type === 'book' ? `Book by ${media.author}` : ''}
                    ${media.media_type === 'cinema' ? `Movie by ${media.director}` : ''}
                    ${media.media_type === 'music' ? `Music by ${media.artist}` : ''}
                </div>
            </div>
        `;
    }

    renderPagination(pagination) {
        const paginationSection = document.getElementById('paginationSection');
        const paginationList = document.getElementById('paginationList');
        
        if (pagination.pages <= 1) {
            paginationSection.style.display = 'none';
            return;
        }
        
        paginationSection.style.display = 'block';
        
        let paginationHTML = '';
        
        // Previous button
        if (pagination.has_prev) {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="diaryManager.goToPage(${pagination.page - 1})">
                        <i class="fas fa-chevron-left"></i> Previous
                    </a>
                </li>
            `;
        }
        
        // Page numbers
        for (let i = 1; i <= pagination.pages; i++) {
            if (i === pagination.page) {
                paginationHTML += `
                    <li class="page-item active">
                        <span class="page-link">${i}</span>
                    </li>
                `;
            } else {
                paginationHTML += `
                    <li class="page-item">
                        <a class="page-link" href="#" onclick="diaryManager.goToPage(${i})">${i}</a>
                    </li>
                `;
            }
        }
        
        // Next button
        if (pagination.has_next) {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="diaryManager.goToPage(${pagination.page + 1})">
                        Next <i class="fas fa-chevron-right"></i>
                    </a>
                </li>
            `;
        }
        
        paginationList.innerHTML = paginationHTML;
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadEntries();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async showEntryDetail(entry) {
        this.currentEntry = entry;
        
        const modalTitle = document.getElementById('detailModalTitle');
        const modalBody = document.getElementById('detailModalBody');
        
        modalTitle.textContent = entry.title || 'Diary Entry';
        
        const date = new Date(entry.created_at).toLocaleString();
        const moodClass = entry.mood ? `mood-${entry.mood}` : 'mood-neutral';
        const moodIcon = this.getMoodIcon(entry.mood);
        const tags = entry.tags.map(tag => `<span class="entry-tag">${tag}</span>`).join('');
        const mediaSection = entry.media ? this.createMediaSection(entry.media) : '';
        const privateBadge = entry.is_private ? '<span class="entry-private">Private</span>' : '';
        
        modalBody.innerHTML = `
            <div class="entry-detail">
                <div class="detail-header">
                    <div class="detail-meta">
                        <div class="detail-mood">
                            <div class="mood-icon ${moodClass}">${moodIcon}</div>
                            ${entry.mood ? this.capitalizeFirst(entry.mood) : 'No mood set'}
                        </div>
                        <div class="detail-date">${date}</div>
                        ${privateBadge}
                    </div>
                </div>
                <div class="detail-content">
                    ${entry.content.replace(/\n/g, '<br>')}
                </div>
                ${tags ? `<div class="detail-tags">${tags}</div>` : ''}
                ${mediaSection}
            </div>
        `;
        
        this.detailModal.show();
    }

    editCurrentEntry() {
        if (this.currentEntry) {
            this.editEntry(this.currentEntry.entry_id);
        }
    }

    async editEntry(entryId) {
        try {
            const response = await fetch(`/api/diary/${entryId}`);
            const data = await response.json();
            
            if (data.success) {
                this.populateEditForm(data.entry);
                this.entryModal.show();
            } else {
                this.showError('Failed to load entry');
            }
        } catch (error) {
            console.error('Error loading entry:', error);
            this.showError('Error loading entry');
        }
    }

    populateEditForm(entry) {
        document.getElementById('entryId').value = entry.entry_id;
        document.getElementById('entryTitle').value = entry.title || '';
        document.getElementById('entryContent').value = entry.content;
        document.getElementById('entryMood').value = entry.mood || '';
        document.getElementById('entryTags').value = entry.tags.join(', ');
        document.getElementById('entryPrivate').checked = entry.is_private;
        document.getElementById('modalTitle').textContent = 'Edit Diary Entry';
    }

    openCreateModal() {
        this.clearForm();
        document.getElementById('modalTitle').textContent = 'New Diary Entry';
        this.entryModal.show();
    }

    clearForm() {
        document.getElementById('entryId').value = '';
        document.getElementById('entryTitle').value = '';
        document.getElementById('entryContent').value = '';
        document.getElementById('entryMood').value = '';
        document.getElementById('entryTags').value = '';
        document.getElementById('entryPrivate').checked = false;
    }

    async saveEntry() {
        const entryId = document.getElementById('entryId').value;
        const title = document.getElementById('entryTitle').value;
        const content = document.getElementById('entryContent').value;
        const mood = document.getElementById('entryMood').value;
        const tags = document.getElementById('entryTags').value.split(',').map(t => t.trim()).filter(t => t);
        const isPrivate = document.getElementById('entryPrivate').checked;
        const mediaId = document.getElementById('entryMedia').value || this.pendingMediaId;

        if (!content.trim()) {
            this.showError('Content is required');
            return;
        }

        const entryData = {
            title: title || null,
            content: content,
            mood: mood || null,
            tags: tags,
            is_private: isPrivate,
            media_id: mediaId || null
        };

        try {
            const url = entryId ? `/api/diary/${entryId}` : '/api/diary';
            const method = entryId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(entryData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.entryModal.hide();
                this.loadEntries();
                this.loadStats();
                this.showSuccess(entryId ? 'Entry updated successfully' : 'Entry created successfully');
                
                // Clear pending media info
                this.pendingMediaId = null;
                
                // Clear URL parameters
                if (window.history.replaceState) {
                    const newUrl = window.location.pathname;
                    window.history.replaceState({}, document.title, newUrl);
                }
            } else {
                this.showError(data.message || 'Failed to save entry');
            }
        } catch (error) {
            console.error('Error saving entry:', error);
            this.showError('Error saving entry');
        }
    }

    async deleteEntry(entryId) {
        if (!confirm('Are you sure you want to delete this diary entry? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/api/diary/${entryId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.success) {
                this.loadEntries();
                this.loadStats();
                this.showSuccess('Entry deleted successfully');
            } else {
                this.showError(data.message || 'Failed to delete entry');
            }
        } catch (error) {
            console.error('Error deleting entry:', error);
            this.showError('Error deleting entry');
        }
    }

    // Utility methods
    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const entriesGrid = document.getElementById('entriesGrid');
        
        if (show) {
            loadingIndicator.style.display = 'block';
            entriesGrid.style.opacity = '0.5';
        } else {
            loadingIndicator.style.display = 'none';
            entriesGrid.style.opacity = '1';
        }
    }

    showError(message) {
        // Create a simple toast notification
        const toast = document.createElement('div');
        toast.className = 'alert alert-danger position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            <i class="fas fa-exclamation-circle"></i> ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    showSuccess(message) {
        const toast = document.createElement('div');
        toast.className = 'alert alert-success position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            <i class="fas fa-check-circle"></i> ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 3000);
    }

    getMoodIcon(mood) {
        const icons = {
            'happy': '😊',
            'sad': '😢',
            'excited': '🤩',
            'calm': '😌',
            'anxious': '😰',
            'inspired': '💡',
            'tired': '😴',
            'energetic': '⚡',
            'neutral': '😐',
            'grateful': '🙏',
            'frustrated': '😤',
            'peaceful': '🕊️'
        };
        return icons[mood] || '📝';
    }

    capitalizeFirst(str) {
        return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    handleUrlParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        const mediaId = urlParams.get('media_id');
        const mediaType = urlParams.get('media_type');
        const mediaTitle = urlParams.get('media_title');
        
        if (mediaId && mediaType && mediaTitle) {
            // Pre-fill the form with media information
            this.openCreateModal();
            document.getElementById('entryTitle').value = `Thoughts on ${mediaTitle}`;
            document.getElementById('entryContent').value = `Just finished ${mediaType === 'book' ? 'reading' : mediaType === 'cinema' ? 'watching' : 'listening to'} "${mediaTitle}". `;
            
            // Store media info for when the entry is saved
            this.pendingMediaId = mediaId;
            
            // Show media link section
            document.getElementById('mediaLinkSection').style.display = 'block';
            document.getElementById('entryMedia').value = mediaId;
        }
    }
}

// Global functions for onclick handlers
function openCreateModal() {
    diaryManager.openCreateModal();
}

function saveEntry() {
    diaryManager.saveEntry();
}

function editCurrentEntry() {
    diaryManager.editCurrentEntry();
}

// Initialize diary manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.diaryManager = new DiaryManager();
});