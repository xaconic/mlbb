(() => {
    const root = document.documentElement;
    const toggle = document.getElementById('theme-toggle');
    const sunIcon = toggle?.querySelector('.theme-icon-sun');
    const moonIcon = toggle?.querySelector('.theme-icon-moon');
    const storageKey = 'mlbb-dashboard-theme';

    if (!toggle || !sunIcon || !moonIcon) {
        return;
    }

    const setTheme = (theme) => {
        const isLight = theme === 'light';
        root.dataset.theme = isLight ? 'light' : 'dark';
        sunIcon.hidden = isLight;
        moonIcon.hidden = !isLight;

        const label = isLight ? 'Switch to dark mode' : 'Switch to light mode';
        toggle.setAttribute('aria-label', label);
        toggle.setAttribute('title', label);
    };

    let savedTheme;
    try {
        savedTheme = window.localStorage.getItem(storageKey);
    } catch (error) {
        console.error('Could not read the saved dashboard theme.', error);
    }

    setTheme(savedTheme === 'light' ? 'light' : 'dark');

    toggle.addEventListener('click', () => {
        const theme = root.dataset.theme === 'light' ? 'dark' : 'light';
        setTheme(theme);
        try {
            window.localStorage.setItem(storageKey, theme);
        } catch (error) {
            console.error('Could not save the dashboard theme.', error);
        }
    });
})();
