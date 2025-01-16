document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Add loading animation to buttons with original text storage
    const buttons = document.querySelectorAll('.btn-primary');
    buttons.forEach(button => {
        // Store original button text
        button.setAttribute('data-original-text', button.innerHTML);

        button.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (!href) return;

            // Store the original button content
            const originalContent = this.innerHTML;

            // Set loading state
            this.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Loading...
            `;

            // Reset button state if navigation is cancelled or fails
            setTimeout(() => {
                if (document.activeElement === this) {
                    this.innerHTML = originalContent;
                }
            }, 500);

            // Handle back button navigation
            window.addEventListener('pageshow', function(event) {
                if (event.persisted) {
                    // Reset all buttons to their original state
                    document.querySelectorAll('.btn-primary').forEach(btn => {
                        const originalText = btn.getAttribute('data-original-text');
                        if (originalText) {
                            btn.innerHTML = originalText;
                        }
                    });
                }
            });
        });
    });

    // Add card animation on scroll
    const cards = document.querySelectorAll('.card');
    const animateCards = () => {
        cards.forEach(card => {
            const cardTop = card.getBoundingClientRect().top;
            const triggerBottom = window.innerHeight * 0.8;

            if (cardTop < triggerBottom) {
                card.classList.add('show');
            }
        });
    };

    window.addEventListener('scroll', animateCards);
    animateCards(); // Initial check

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.card');

            cards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        }, 300));
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Progress bar for activity points
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 100);
    });
});

// Utility function for debouncing
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

// Notification system
const NotificationSystem = {
    show: function(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.body.appendChild(alert);

        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
};

// Dark mode toggle
const darkModeToggle = document.querySelector('.dark-mode-toggle');
if (darkModeToggle) {
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });
}