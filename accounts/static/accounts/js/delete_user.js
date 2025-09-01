document.addEventListener('DOMContentLoaded', function () {
  var deleteModal = document.getElementById('deleteConfirmationModal');
  deleteModal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget;
    
    var userName = button.getAttribute('data-user-name');
    var deleteUrl = button.getAttribute('data-user-delete-url');
    
    var modalNameSpan = deleteModal.querySelector('#userNameToDelete');
    var deleteForm = deleteModal.querySelector('#deleteForm');
    
    modalNameSpan.textContent = userName;
    deleteForm.action = deleteUrl;
  });
});