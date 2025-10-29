document.addEventListener('DOMContentLoaded', function () {
    const formsetContainer = document.getElementById('instructor-forms');
    const addButton = document.getElementById('add-instructor-row');
    const removeButton = document.getElementById('remove-last-instructor-row');
    const emptyFormTemplate = document.getElementById('empty-instructor-form');
    const totalFormsInput = document.querySelector('input[name="instruktur_set-TOTAL_FORMS"]');

    // --- Basic Checks ---
    if (!formsetContainer || !addButton || !removeButton || !emptyFormTemplate || !totalFormsInput) {
        console.warn("Formset elements for dynamic rows not found, script disabled.");
        return;
    }
    console.log("Dynamic formset script initialized (Single Remove Button).");

    // --- ADD ROW ---
    addButton.addEventListener('click', function () {
        console.log("Add button clicked.");
        let currentFormCount = parseInt(totalFormsInput.value);
        console.log("Current TOTAL_FORMS:", currentFormCount);

        // Clone the empty form template's CONTENT
        const newFormRow = emptyFormTemplate.cloneNode(true);
        newFormRow.id = `instructor-row-${currentFormCount}`;
        newFormRow.classList.remove('d-none');
        console.log("Cloned form, removed 'd-none'.");

        // Update indices in the cloned row's children ('__prefix__' is the placeholder)
        const indexRegex = new RegExp('__prefix__', 'g');
        newFormRow.querySelectorAll('input, select, textarea, label, div[id*="__prefix__"]').forEach(el => {
            ['id', 'name', 'for'].forEach(attr => {
                if (el.hasAttribute(attr)) {
                    el.setAttribute(attr, el.getAttribute(attr).replace(indexRegex, currentFormCount));
                }
            });
        });
        console.log("Replaced '__prefix__' with index:", currentFormCount);

        // --- FIX: COPY OPTIONS TO THE NEW SELECT ---
        const newSelect = newFormRow.querySelector('select[name$="-instruktur"]');
        if (newSelect) {
            // Find the *first visible* existing instructor select to copy options from
            const firstExistingSelect = formsetContainer.querySelector('.instructor-form-row:not([style*="display: none"]) select[name$="-instruktur"]');
            
            if (firstExistingSelect) {
                console.log("Copying options from first select:", firstExistingSelect);
                // Clear any potentially empty/default options from the new select first
                newSelect.innerHTML = ''; 
                // Iterate through options of the existing select and clone them
                Array.from(firstExistingSelect.options).forEach(option => {
                    newSelect.appendChild(option.cloneNode(true));
                });
                console.log("Options copied to new select.");
                 // Ensure the default "---" or empty option is selected if it exists
                if (newSelect.options.length > 0 && newSelect.options[0].value === "") {
                   newSelect.selectedIndex = 0;
                }
            } else {
                console.warn("Could not find an existing select to copy options from.");
                // Optionally clear the new select if no source is found
                 newSelect.innerHTML = '<option value="">--- No instructors available ---</option>';
            }
        } else {
            console.error("Could not find the new select element in the cloned row.");
        }
        // --- END FIX ---

        formsetContainer.appendChild(newFormRow);
        console.log("Appended new form row to container.");

        totalFormsInput.value = currentFormCount + 1;
        console.log("Updated TOTAL_FORMS to:", totalFormsInput.value);
        toggleRemoveButton();
    });

    // --- REMOVE LAST ROW --- (Code remains the same as your last version)
    removeButton.addEventListener('click', function() {
         console.log("Remove button clicked.");
         const visibleRows = formsetContainer.querySelectorAll('.instructor-form-row:not([style*="display: none"])');
         console.log("Found", visibleRows.length, "visible rows.");

         if (visibleRows.length > 0) { 
             const lastRow = visibleRows[visibleRows.length - 1]; 
             const deleteCheckbox = lastRow.querySelector('input[type="checkbox"][name$="-DELETE"]');

             if (deleteCheckbox) {
                 deleteCheckbox.checked = true;
                 lastRow.style.display = 'none'; 
                 console.log("Hid last visible existing form row and checked DELETE.");
             } else {
                 lastRow.remove();
                 console.log("Removed last visible newly added form row.");
                 totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
                 console.log("Decremented TOTAL_FORMS to:", totalFormsInput.value);
             }
         } else {
             console.log("No visible rows left to remove.");
         }
         toggleRemoveButton(); 
     });


    // --- Function to Enable/Disable Remove Button --- (Code remains the same)
     function toggleRemoveButton() {
         const visibleRowsCount = formsetContainer.querySelectorAll('.instructor-form-row:not([style*="display: none"])').length;
         removeButton.disabled = visibleRowsCount <= 1; 
         console.log("Visible rows:", visibleRowsCount, "Remove button disabled:", removeButton.disabled);
     }

    // --- Initial State --- (Code remains the same)
    toggleRemoveButton(); 

});