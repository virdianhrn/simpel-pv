document.addEventListener('DOMContentLoaded', function () {
    const deleteModal = document.getElementById('deleteConfirmationModal');
    
    // Check if the modal exists on the page before adding an event listener
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            // Button that triggered the modal
            const button = event.relatedTarget;

            // Extract info from data-* attributes
            const deleteUrl = button.getAttribute('data-delete-url');
            const tahunNama = button.getAttribute('data-tahun-nama');

            // Find the elements inside the modal to update
            const modalForm = deleteModal.querySelector('#deleteForm');
            const modalBodyText = deleteModal.querySelector('#tahunNameToDelete');

            // Update the modal's content
            modalForm.action = deleteUrl;
            modalBodyText.textContent = tahunNama;
        });
    }
});