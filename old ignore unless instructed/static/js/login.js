document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    // If user is already logged in, redirect to admin page
    if (localStorage.getItem('access_token')) {
        window.location.href = '/admin';
    }

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        errorMessage.style.display = 'none';
        errorMessage.textContent = '';

        const username = loginForm.username.value;
        const password = loginForm.password.value;

        // FastAPI's OAuth2PasswordRequestForm expects form data, not JSON
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch('/api/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Login failed');
            }

            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);

            // Redirect to the dashboard on successful login
            window.location.href = '/';

        } catch (error) {
            errorMessage.textContent = `Error: ${error.message}`;
            errorMessage.style.display = 'block';
        }
    });
});
