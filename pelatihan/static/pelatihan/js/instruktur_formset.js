// pelatihan/static/pelatihan/js/dynamic_formset.js

document.addEventListener('DOMContentLoaded', function () {
    const formsetContainer = document.getElementById('instructor-forms');
    const addButton = document.getElementById('add-instructor-row');
    const removeButton = document.getElementById('remove-last-instructor-row'); // New button
    const emptyFormTemplate = document.getElementById('empty-instructor-form');
    const totalFormsInput = document.querySelector('input[name="instruktur_set-TOTAL_FORMS"]'); 

    // --- Basic Checks ---
    if (!formsetContainer || !addButton || !removeButton || !emptyFormTemplate || !totalFormsInput) {
        console.warn("Formset elements for dynamic rows not found, script disabled.");
        return; 
    }
    console.log("Dynamic formset script initialized (Single Remove Button).");
    
    // --- ADD ROW --- (Remains mostly the same, no remove listener needed here)
    addButton.addEventListener('click', function () {
        let currentFormCount = parseInt(totalFormsInput.value); 
        const newForm = emptyFormTemplate.cloneNode(true);
        newForm.id = `instructor-row-${currentFormCount}`; 
        newForm.classList.remove('d-none'); 
        const indexRegex = new RegExp('__prefix__', 'g');
        newForm.innerHTML = newForm.innerHTML.replace(indexRegex, currentFormCount);
        formsetContainer.appendChild(newForm);
        totalFormsInput.value = currentFormCount + 1;
        toggleRemoveButton(); // Check if remove button should be enabled/disabled
    });

    // --- REMOVE LAST ROW --- (New logic)
    removeButton.addEventListener('click', function() {
        const visibleRows = formsetContainer.querySelectorAll('.instructor-form-row:not([style*="display: none"])');
        
        if (visibleRows.length > 0) { // Only remove if more than one row exists
            const lastRow = visibleRows[visibleRows.length - 1]; // Get the last visible row
            const deleteCheckbox = lastRow.querySelector('input[type="checkbox"][name$="-DELETE"]');

            if (deleteCheckbox) {
                // It's an existing form, check DELETE and hide
                deleteCheckbox.checked = true;
                lastRow.style.display = 'none'; 
                console.log("Hid last existing form row.");
                // DO NOT decrement totalFormsInput for hidden existing forms
            } else {
                // It's a newly added form, remove completely
                lastRow.remove();
                console.log("Removed last newly added form row.");
                // Decrement total forms count
                totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
            }
        } else {
            console.log("Cannot remove the last row.");
            // Optionally provide feedback to the user
            // alert("Minimal harus ada satu baris instruktur."); 
        }
        toggleRemoveButton(); // Update button state after removal
    });

    // --- Function to Enable/Disable Remove Button ---
    function toggleRemoveButton() {
        const visibleRowsCount = formsetContainer.querySelectorAll('.instructor-form-row:not([style*="display: none"])').length;
        removeButton.disabled = visibleRowsCount <= 0; // Disable if no rows visible
    }

    // --- Initial State ---
    toggleRemoveButton(); // Set initial state of the remove button on page load

});