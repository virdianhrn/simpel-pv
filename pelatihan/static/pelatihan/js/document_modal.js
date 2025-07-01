document.addEventListener('DOMContentLoaded', function() {
    const documentModal = document.getElementById('documentModal');
    const documentIframe = document.getElementById('documentIframe');
    const downloadDocumentBtn = document.getElementById('downloadDocumentBtn');
    const documentModalLabel = document.getElementById('documentModalLabel');

    documentModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const documentUrl = button.getAttribute('data-document-url');
        const documentTitle = button.getAttribute('data-document-title');

        documentIframe.src = documentUrl;
        downloadDocumentBtn.href = documentUrl;
        documentModalLabel.textContent = documentTitle;
    });

    documentModal.addEventListener('hidden.bs.modal', function () {
        documentIframe.src = '';
        downloadDocumentBtn.href = '#';
    });
});
