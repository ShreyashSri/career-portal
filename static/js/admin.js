// Admin Panel JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // ... (keep existing datepicker and notification code) ...

    // Handle delete confirmations for applications
    const deleteButtons = document.querySelectorAll('.delete-btn');
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
                        // Remove the row from the table
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

    // Handle bulk actions for applications
    const bulkActionSelect = document.querySelector('.bulk-action-select');
    const selectAllCheckbox = document.querySelector('.select-all');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    
    // Handle "Select All" checkbox
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }

    // Handle bulk actions
    if (bulkActionSelect) {
        bulkActionSelect.addEventListener('change', function() {
            const selectedAction = this.value;
            if (!selectedAction) return;

            const selectedIds = Array.from(itemCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            
            if (selectedIds.length === 0) {
                showNotification('Please select applications to perform action', 'warning');
                this.value = '';
                return;
            }

            const actionText = {
                'approve': 'approve',
                'reject': 'reject',
                'delete': 'delete'
            }[selectedAction];

            if (confirm(`Are you sure you want to ${actionText} the selected applications?`)) {
                fetch('/admin/applications/bulk-action', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'action': selectedAction,
                        'ids[]': selectedIds
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message, 'success');
                        location.reload(); // Refresh to show updated status
                    } else {
                        showNotification(data.message || 'Error performing bulk action', 'error');
                    }
                })
                .catch(error => {
                    showNotification('Error performing bulk action', 'error');
                });
            }
            
            this.value = '';
        });
    }

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

    // Keep existing search functionality and debounce helper...
});