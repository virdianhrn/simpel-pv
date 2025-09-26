document.addEventListener('DOMContentLoaded', function () {
  var deleteModal = document.getElementById('deleteConfirmationModal');
  deleteModal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget; // Button that triggered the modal
    
    // Extract info from data-* attributes
    var pelatihanName = button.getAttribute('data-pelatihan-name');
    var deleteUrl = button.getAttribute('data-pelatihan-delete-url');
    
    // Update the modal's content
    var modalNameSpan = deleteModal.querySelector('#pelatihanNameToDelete');
    var deleteForm = deleteModal.querySelector('#deleteForm');
    
    modalNameSpan.textContent = pelatihanName;
    deleteForm.action = deleteUrl;
  });
});