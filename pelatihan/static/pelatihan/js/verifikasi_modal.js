document.addEventListener('DOMContentLoaded', function() {
    const documentModal = document.getElementById('documentModal');
    const documentModalLabel = document.getElementById('documentModalLabel');
    const iframeContainer = document.getElementById('iframeContainer');
    const originalIframeHtml = iframeContainer.innerHTML; // Save the pristine iframe tag
    const documentFormContainer = document.getElementById('documentFormContainer');

    documentModal.addEventListener('show.bs.modal', async function (event) {
        const button = event.relatedTarget;
        const documentId = button.getAttribute('data-document-id');
        const documentTitle = button.getAttribute('data-document-title');
        const pelatihanId = button.getAttribute('data-pelatihan-id');
        const documentUrl = button.getAttribute('data-document-url');
        const documentPreviewIframe = document.getElementById('documentPreviewIframe');
        
        documentModalLabel.textContent = `Edit & Pratinjau: ${documentTitle}`;
        documentPreviewIframe.src = documentUrl;

        try {
            const response = await fetch(`/pelatihan/${pelatihanId}/verifikasi/${documentId}`);
            const formHtml = await response.text();
            documentFormContainer.innerHTML = formHtml;
        } catch (error) {
            documentFormContainer.innerHTML = '<p class="text-danger">Gagal memuat form. Silakan coba lagi.</p>';
            console.error('Error fetching form:', error);
        }
    });

    document.addEventListener('submit', async function(event) {
        if (event.target.id === 'editDocumentForm') {
            event.preventDefault(); 
            const form = event.target;
            const formData = new FormData(form);
            const url = form.action;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-CSRFToken': formData.get('csrfmiddlewaretoken') }
                });

                const result = await response.json();
                if (result.success) {
                    location.reload(); 
                } else {
                    alert('Gagal menyimpan. Periksa kembali isian Anda.');
                }
            } catch (error) {
                console.log(error)
                alert('Terjadi kesalahan. Silakan coba lagi.');
            }
        }
    });
    
    // 3. When the modal is hidden, clear both the iframe and the form
    documentModal.addEventListener('hidden.bs.modal', function () {
        iframeContainer.innerHTML = originalIframeHtml;
        documentFormContainer.innerHTML = ''; // Clear the form container
    });
});