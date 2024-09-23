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
