document.addEventListener('DOMContentLoaded', function() {
    // Find all skip buttons on the page
    document.querySelectorAll('.skip-button').forEach(button => {
        button.addEventListener('click', function(event) {
            // 1. Stop the link from making a normal GET request
            event.preventDefault();

            // 2. Find the CSRF token from the main form rendered by Django
            const csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (!csrfTokenInput) {
                console.error('CSRF token not found!');
                return;
            }
            const csrfToken = csrfTokenInput.value;

            // 3. Create a new, temporary form in memory
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = this.href; // The URL comes from the button's href

            // 4. Create a hidden input for the CSRF token
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken; // Use the REAL token value we found
            form.appendChild(csrfInput);

            // 5. Add the form to the page and submit it
            document.body.appendChild(form);
            form.submit();
        });
    });
});