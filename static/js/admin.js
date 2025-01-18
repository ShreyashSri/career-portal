console.log('JavaScript file loaded');

// Debug helper
function debug(message) {
    console.log(`Debug: ${message}`);
}

document.addEventListener('DOMContentLoaded', function() {
    debug('Admin JS loaded');

    // ====== Element Selectors ======
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');
    const typeFilter = document.querySelector('#type-filter');
    const searchableItems = document.querySelectorAll('.searchable-item');
    const selectAllCheckbox = document.querySelector('.select-all');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    const deleteButtons = document.querySelectorAll('.delete-btn');

    // Log initial element detection
    debug(`Found ${searchableItems.length} searchable rows`);
    if (searchInput) debug('Search input found');
    if (searchBtn) debug('Search button found');
    if (typeFilter) debug('Type filter found');

    // ====== Utility Functions ======
    function debounce(func, wait) {
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

    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // ====== Search and Filter Functions ======
    function performSearch() {
        debug('Performing search');
        const searchTerm = searchInput.value.toLowerCase();
        const selectedType = typeFilter ? typeFilter.value.toLowerCase() : '';
        
        searchableItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            const typeCell = item.querySelector('td:nth-child(3)');
            const type = typeCell ? typeCell.textContent.trim().toLowerCase() : '';
            
            const matchesSearch = searchTerm === '' || text.includes(searchTerm);
            const matchesType = !selectedType || type === selectedType;
            
            item.style.display = matchesSearch && matchesType ? '' : 'none';
        });

        updateNoResultsMessage();
    }

    function updateNoResultsMessage() {
        const tableBody = document.querySelector('tbody');
        let noResultsMsg = document.querySelector('.no-results-message');
        
        const hasVisibleRows = Array.from(searchableItems)
            .some(item => item.style.display !== 'none');
        
        if (!hasVisibleRows) {
            if (!noResultsMsg) {
                noResultsMsg = document.createElement('tr');
                noResultsMsg.className = 'no-results-message';
                noResultsMsg.innerHTML = `
                    <td colspan="100%" class="text-center py-4">
                        No matching results found
                    </td>
                `;
                tableBody.appendChild(noResultsMsg);
            }
        } else if (noResultsMsg) {
            noResultsMsg.remove();
        }
    }

    // ====== Event Listeners ======

    // Search functionality
    const debouncedSearch = debounce(performSearch, 300);
    
    if (searchInput) {
        // Real-time search as user types
        searchInput.addEventListener('input', debouncedSearch);
        
        // Search on Enter key
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                debug('Enter key pressed');
                performSearch();
            }
        });
    }

    if (searchBtn) {
        console.log('Search button found and event listener being added');
        searchBtn.addEventListener('click', function(e) {
            console.log('Button clicked - event fired');
            e.preventDefault();
            console.log('Search term:', searchInput.value);
            performSearch();
        });
    } else {
        console.log('Search button NOT found in DOM');
    }

    if (typeFilter) {
        typeFilter.addEventListener('change', function() {
            debug('Type filter changed');
            performSearch();
        });
    }

    // Select All checkbox functionality
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            debug('Select all checkbox changed');
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }

    // Delete button functionality
    deleteButtons.forEach((button, index) => {
        debug(`Found delete button ${index} with ID: ${button.dataset.id}`);
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            debug('Delete button clicked');
            
            const applicationId = this.dataset.id;
            debug(`Attempting to delete application: ${applicationId}`);
            
            if (!applicationId) {
                debug('Error: No application ID found on button');
                showNotification('Error: Could not identify application', 'error');
                return;
            }
            
            if (confirm('Are you sure you want to delete this application?')) {
                debug('User confirmed delete');
                
                fetch(`/admin/applications/delete/${applicationId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => {
                    debug(`Server response status: ${response.status}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    debug('Received response:', data);
                    if (data.success) {
                        const row = this.closest('tr');
                        if (row) {
                            row.remove();
                            debug('Row removed from table');
                            showNotification(data.message || 'Application deleted successfully', 'success');
                        } else {
                            throw new Error('Could not find table row to remove');
                        }
                    } else {
                        throw new Error(data.message || 'Server indicated deletion failed');
                    }
                })
                .catch(error => {
                    debug('Delete error:', error);
                    showNotification(error.message || 'Error deleting application', 'error');
                });
            }
        });
    });

    // Status toggle functionality
    const statusToggles = document.querySelectorAll('.status-toggle');
    statusToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const opportunityId = this.dataset.id;
            const newStatus = this.checked ? 'active' : 'inactive';
            
            fetch(`/admin/opportunities/${opportunityId}/status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(`Status updated to ${newStatus}`, 'success');
                } else {
                    showNotification(data.message || 'Error updating status', 'error');
                    // Revert the toggle if there was an error
                    this.checked = !this.checked;
                }
            })
            .catch(error => {
                showNotification('Error updating status', 'error');
                // Revert the toggle on error
                this.checked = !this.checked;
            });
        });
    });

    // Initialize search if there are any existing values
    if (searchInput?.value || typeFilter?.value) {
        performSearch();
    }
});