console.log('Admin JS file loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    
    // Get elements
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');
    const typeFilter = document.querySelector('#type-filter');
    const searchableItems = document.querySelectorAll('.searchable-item');
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const statusToggles = document.querySelectorAll('.status-toggle');
    const selectAllCheckbox = document.querySelector('.select-all');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    
    console.log('Search button:', searchBtn);
    console.log('Found searchable items:', searchableItems.length);
    
    // Search function
    function performSearch() {
        console.log('Performing search');
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
        }
        
        // Add event listeners
        if (searchBtn) {
            searchBtn.addEventListener('click', function(e) {
                console.log('Search button clicked');
                e.preventDefault();
                performSearch();
            });
        }
        
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    console.log('Enter pressed');
                    performSearch();
                }
            });

        updateNoResultsMessage();
    }

    // Show/hide no results message
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

    // Notification function
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Event Listeners
    if (searchBtn) {
        searchBtn.addEventListener('click', function(e) {
            console.log('Search button clicked');
            e.preventDefault();
            performSearch();
        });
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                console.log('Enter pressed');
                performSearch();
            }
        });
    }
    
    if (typeFilter) {
        typeFilter.addEventListener('change', function() {
            console.log('Filter changed');
            performSearch();
        });
    }

    // Select All functionality
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }

    // Delete functionality
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const applicationId = this.dataset.id;
            
            if (confirm('Are you sure you want to delete this application?')) {
                fetch(`/admin/applications/delete/${applicationId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message, 'success');
                        this.closest('tr').remove();
                    } else {
                        showNotification(data.message || 'Error deleting application', 'error');
                    }
                })
                .catch(error => {
                    showNotification('Error deleting application', 'error');
                });
            }
        });
    });

    // Status toggle functionality
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
                    this.checked = !this.checked;
                }
            })
            .catch(error => {
                showNotification('Error updating status', 'error');
                this.checked = !this.checked;
            });
        });
    });
});