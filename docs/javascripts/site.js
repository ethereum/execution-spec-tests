function initializeDataTables() {
    if (!$.fn.DataTable.isDataTable('#test_table')) {
        $('#test_table').DataTable({
            pageLength: -1,
            scrollX: true,
            autoWidth: false
        });
    }
}

// Use MutationObserver to detect changes in the DOM
const observer = new MutationObserver((mutationsList, observer) => {
    for (let mutation of mutationsList) {
        if (mutation.type === 'childList') {
            initializeDataTables();
        }
    }
});

// Start observing the body element for changes in child elements, this is required to 
// initialize the DataTables when navigating between pages
observer.observe(document.body, { childList: true, subtree: true });

// Run on initial load
document.addEventListener('DOMContentLoaded', function() {
    initializeDataTables();
});

// Event delegation for copy-to-clipboard functionality
document.addEventListener('click', function(event) {
    if (event.target && event.target.classList.contains('copy-id')) {
        const fullId = event.target.getAttribute('data-full-id');

        // Copy to clipboard
        navigator.clipboard.writeText(fullId).then(() => {
            const originalContent = event.target.innerHTML;

            // Set the sliding message with animation
            event.target.innerHTML = '<span class="slide show">...full test id copied!</span>';

            // Delay the hiding of the slide-out message
            setTimeout(() => {
                const slideElement = event.target.querySelector('.slide');
                if (slideElement) {
                    slideElement.classList.add('hide');
                }
            }, 1000);

            // Restore the original content after the animation
            setTimeout(() => {
                event.target.innerHTML = originalContent;
            }, 1500);  // Total duration before restoring original content
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
});