document.addEventListener('DOMContentLoaded', function () {
    // 1. Select the body element and get the data from the attribute
    const body = document.querySelector('body');
    const messagesJson = body.dataset.messages;

    // 2. Check if there are any messages
    if (!messagesJson || messagesJson === '[]') {
        return; // Exit if no messages
    }

    // 3. Parse the JSON string back into a JavaScript array
    const messages = JSON.parse(messagesJson);

    // Get the toast elements from the DOM
    const toastEl = document.getElementById('appToast');
    const toastHeader = document.getElementById('toastHeader');
    const toastTitle = document.getElementById('toastTitle');
    const toastIcon = document.getElementById('toastIcon');
    const toastBody = document.getElementById('toastBody');
    const appToast = new bootstrap.Toast(toastEl, { delay: 5000 });

    let messagesHtml = '';
    let messageLevel = 'info'; // Default level

    // 4. Loop through the parsed messages
    messages.forEach(message => {
        messagesHtml += message.body + '<br>';
        if (message.tags.includes('error')) {
            messageLevel = 'error';
        } else if (message.tags.includes('success') && messageLevel !== 'error') {
            messageLevel = 'success';
        }
    });

    // Customize and show the toast
    if (messageLevel === 'error') {
        toastHeader.className = 'toast-header bg-danger text-white';
        toastTitle.textContent = 'Gagal Mengunggah';
        toastIcon.className = 'fa-solid fa-circle-exclamation me-2';
    } else if (messageLevel === 'success') {
        toastHeader.className = 'toast-header bg-success text-white';
        toastTitle.textContent = 'Berhasil';
        toastIcon.className = 'fa-solid fa-circle-check me-2';
    }

    toastBody.innerHTML = messagesHtml;
    appToast.show();
});