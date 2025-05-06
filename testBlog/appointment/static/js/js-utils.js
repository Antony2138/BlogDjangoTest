function setupMessageAutoDismiss() {
    const messageElements = document.querySelectorAll('.alert-dismissible');
    messageElements.forEach(function(element) {
        setTimeout(() => {
            element.style.opacity = '0';
            setTimeout(() => element.remove(), 300);
        }, 5000);
    });
}

document.addEventListener('DOMContentLoaded', setupMessageAutoDismiss);

document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'render-chunk' ||
        evt.detail.target === document.body) {
        setupMessageAutoDismiss();
    }
});
