// Function to initialize DataTables
function initializeDataTables() {
    if (!$.fn.DataTable.isDataTable('#test_table')) {
        $('#test_table').DataTable({
            pageLength: -1,
            scrollX: true,
            autoWidth: false
        });
    }
}

// Function to attach event listeners to the selectors
function attachFilterListeners() {

    // Attach change event listeners
    $('#fork_selector').off('change').on('change', filterTable);
    $('#fixture_selector').off('change').on('change', filterTable);
}

// Function to filter table based on selected fork and fixture type
function filterTable() {
    var selectedFork = $('#fork_selector').val();
    var selectedFixture = $('#fixture_selector').val();

    $('#test_table tbody tr').each(function() {
        var fork = $(this).attr('data-fork');
        var fixture = $(this).attr('data-fixture');

        // Show/Hide rows based on the selected fork and fixture type
        var showRow = (selectedFork === 'all' || fork === selectedFork) &&
                        (selectedFixture === 'all' || fixture === selectedFixture);

        $(this).toggle(showRow);  // Show or hide the row
    });
}

// Function to apply default filters on page load or navigation
function applyDefaultFilters() {
    // Trigger the filtering function on page load or navigation
    filterTable();
}

// Use MutationObserver to detect changes in the DOM and reinitialize DataTables and filters
const observer = new MutationObserver((mutationsList, observer) => {
    for (let mutation of mutationsList) {
        if (mutation.type === 'childList') {
            initializeDataTables();
            attachFilterListeners();
            applyDefaultFilters();
        }
    }
});

// Start observing the body element for changes in child elements
observer.observe(document.body, { childList: true, subtree: true });

// Run on initial load
document.addEventListener('DOMContentLoaded', function() {
    initializeDataTables();
    attachFilterListeners();
    applyDefaultFilters();
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
