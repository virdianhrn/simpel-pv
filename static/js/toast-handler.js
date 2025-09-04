document.addEventListener('DOMContentLoaded', function () {
    const body = document.querySelector('body');
    const messagesJson = body.dataset.messages;

    if (!messagesJson || messagesJson === '[]') {
        return; // Exit if no messages
    }

    const messages = JSON.parse(messagesJson);
    const toastEl = document.getElementById('appToast');
    const toastHeader = document.getElementById('toastHeader');
    const toastTitle = document.getElementById('toastTitle');
    const toastIcon = document.getElementById('toastIcon');
    const toastBody = document.getElementById('toastBody');
    const appToast = new bootstrap.Toast(toastEl, { delay: 5000 });

    let messagesHtml = '';
    let messageLevel = 'info';

    messages.forEach(message => {
        messagesHtml += message.body + '<br>';
        if (message.tags.includes('error')) {
            messageLevel = 'error';
        } else if (message.tags.includes('success') && messageLevel !== 'error') {
            messageLevel = 'success';
        }
    });

    // Reset styles before applying new ones
    toastHeader.className = 'toast-header'; 
    toastIcon.className = 'me-2';

    if (messageLevel === 'error') {
        toastHeader.classList.add('bg-danger', 'text-white');
        toastTitle.textContent = 'Error';
        toastIcon.classList.add('fa-solid', 'fa-circle-exclamation');
    } else if (messageLevel === 'success') {
        toastHeader.classList.add('bg-success', 'text-white');
        toastTitle.textContent = 'Berhasil';
        toastIcon.classList.add('fa-solid', 'fa-circle-check');
    } else {
        toastHeader.classList.add('bg-info', 'text-white');
        toastTitle.textContent = 'Pemberitahuan';
        toastIcon.classList.add('fa-solid', 'fa-circle-info');
    }
    
    toastBody.innerHTML = messagesHtml;
    appToast.show();
});