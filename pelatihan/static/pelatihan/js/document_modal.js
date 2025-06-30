document.addEventListener('DOMContentLoaded', function() {
    const documentModal = document.getElementById('documentModal');
    const documentIframe = document.getElementById('documentIframe');
    const downloadDocumentBtn = document.getElementById('downloadDocumentBtn');

    documentModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const documentUrl = button.getAttribute('data-document-url');

        documentIframe.src = documentUrl;

        downloadDocumentBtn.href = documentUrl;
    });

    documentModal.addEventListener('hidden.bs.modal', function () {
        documentIframe.src = '';
        downloadDocumentBtn.href = '#';
    });
});
