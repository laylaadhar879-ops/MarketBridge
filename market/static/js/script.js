(function () {
    const toggleButton = document.getElementById('searchToggle');
    const searchForm = document.getElementById('navSearch');
    const searchInput = document.getElementById('navSearchInput');

    if (!toggleButton || !searchForm || !searchInput) {
        return;
    }

    toggleButton.addEventListener('click', function () {
        const isOpen = searchForm.classList.toggle('is-open');
        if (isOpen) {
            searchInput.focus();
        }
    });

    document.addEventListener('click', function (event) {
        const clickedInsideSearch = searchForm.contains(event.target) || toggleButton.contains(event.target);
        if (!clickedInsideSearch) {
            searchForm.classList.remove('is-open');
        }
    });
})();
