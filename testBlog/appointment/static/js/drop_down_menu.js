<script>
document.addEventListener('DOMContentLoaded', function () {
    const dropdown = document.querySelector('.dropdown-toggle');
    const parent = dropdown.closest('.dropdown');

    if (dropdown && parent) {
        parent.addEventListener('mouseenter', function () {
            dropdown.classList.add('show');
            dropdown.setAttribute('aria-expanded', 'true');
            const menu = parent.querySelector('.dropdown-menu');
            if (menu) menu.classList.add('show');
        });

        parent.addEventListener('mouseleave', function () {
            dropdown.classList.remove('show');
            dropdown.setAttribute('aria-expanded', 'false');
            const menu = parent.querySelector('.dropdown-menu');
            if (menu) menu.classList.remove('show');
        });
    }
});
</script>
