// Admin Panel JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any datepickers
    const datepickers = document.querySelectorAll('.datepicker');
    datepickers.forEach(dp => {
        // Add your preferred datepicker initialization here
    });

    // Handle delete confirmations
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Handle status updates
    const statusToggles = document.querySelectorAll('.status-toggle');
    statusToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const itemId = this.dataset.id;
            const newStatus = this.checked ? 'active' : 'inactive';
            
            fetch(`/admin/update-status/${itemId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Status updated successfully', 'success');
                } else {
                    showNotification('Error updating status', 'error');
                    // Revert toggle if update failed
                    this.checked = !this.checked;
                }
            })
            .catch(error => {
                showNotification('Error updating status', 'error');
                this.checked = !this.checked;
            });
        });
    });

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.toLowerCase();
            const items = document.querySelectorAll('.searchable-item');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    }

    // Debounce helper function
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

    // Bulk actions
    const bulkActionSelect = document.querySelector('.bulk-action-select');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    
    if (bulkActionSelect) {
        bulkActionSelect.addEventListener('change', function() {
            const selectedAction = this.value;
            const selectedItems = Array.from(itemCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            
            if (selectedItems.length === 0) {
                showNotification('Please select items to perform action', 'warning');
                this.value = '';
                return;
            }

            if (confirm(`Are you sure you want to ${selectedAction} the selected items?`)) {
                executeBulkAction(selectedAction, selectedItems);
            }
            
            this.value = '';
        });
    }

    // Execute bulk actions
    function executeBulkAction(action, items) {
        fetch('/admin/bulk-action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: action,
                items: items
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Bulk action completed successfully', 'success');
                // Refresh the page or update UI as needed
                location.reload();
            } else {
                showNotification('Error performing bulk action', 'error');
            }
        })
        .catch(error => {
            showNotification('Error performing bulk action', 'error');
        });
    }
});