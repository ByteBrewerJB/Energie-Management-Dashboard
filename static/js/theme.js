// static/js/theme.js
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const themeLabel = document.getElementById('theme-label');
    const body = document.body;

    const applyTheme = (theme) => {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
            if(themeToggle) themeToggle.checked = true;
            if(themeLabel) themeLabel.textContent = 'Dark Mode';
        } else {
            body.classList.remove('dark-mode');
            if(themeToggle) themeToggle.checked = false;
            if(themeLabel) themeLabel.textContent = 'Light Mode';
        }
    };

    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Load saved theme, or default to dark as requested for admin, or system preference
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        // Default to dark mode for the admin page as per user request
        if (window.location.pathname.includes('/admin')) {
             applyTheme('dark');
        } else if (prefersDark) {
            applyTheme('dark');
        } else {
            applyTheme('light');
        }
    }


    if(themeToggle) {
        themeToggle.addEventListener('change', () => {
            if (themeToggle.checked) {
                applyTheme('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                applyTheme('light');
                localStorage.setItem('theme', 'light');
            }
        });
    }
});
