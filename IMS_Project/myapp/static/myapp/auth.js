(() => {
    document.querySelectorAll('[data-password-toggle]').forEach((toggle) => {
        const input = document.getElementById(toggle.dataset.passwordToggle);
        if (!input) {
            return;
        }

        toggle.addEventListener('click', () => {
            const reveal = input.type === 'password';
            input.type = reveal ? 'text' : 'password';
            const action = reveal ? 'Hide' : 'Show';
            toggle.setAttribute('aria-label', `${action} password`);
            toggle.setAttribute('aria-pressed', String(reveal));

            const screenReaderText = toggle.querySelector('.sr-only');
            toggle.classList.toggle('is-visible', reveal);
            if (screenReaderText) {
                screenReaderText.textContent = `${action} password`;
            }
        });
    });
})();
