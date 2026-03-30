/* IoT Security Learning Tool - Client-side JavaScript */

/**
 * Update user progress via the API.
 */
function updateProgress(itemType, itemId, status) {
    fetch('/api/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            item_type: itemType,
            item_id: itemId,
            status: status,
        }),
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to update progress');
        return response.json();
    })
    .then(data => {
        const item = document.querySelector(
            `.progress-item[data-type="${itemType}"][data-id="${itemId}"]`
        );
        if (item) {
            item.classList.remove('status-not_started', 'status-in_progress', 'status-completed');
            item.classList.add(`status-${status}`);
        }
    })
    .catch(err => {
        console.error('Progress update failed:', err);
        alert('Failed to save progress. Are you logged in?');
    });
}

/* Smooth scroll for anchor links within articles */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.article-body a[href^="#"]').forEach(function (link) {
        link.addEventListener('click', function (e) {
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});
