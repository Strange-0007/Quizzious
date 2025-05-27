document.addEventListener('DOMContentLoaded', function() {
    // Login form validation
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            let isValid = true;
            const username = document.getElementById('username');
            const password = document.getElementById('password');
            
            // Reset any previous error messages
            document.querySelectorAll('.invalid-feedback').forEach(el => {
                el.textContent = '';
            });
            document.querySelectorAll('.is-invalid').forEach(el => {
                el.classList.remove('is-invalid');
            });
            
            // Validate username
            if (!username.value.trim()) {
                isValid = false;
                username.classList.add('is-invalid');
                // Find the invalid feedback element
                const usernameFeedback = username.closest('.input-group').querySelector('.invalid-feedback');
                if (usernameFeedback) {
                    usernameFeedback.textContent = 'Username is required';
                }
            }
            
            // Validate email format
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (username.value.trim() && !emailRegex.test(username.value)) {
                isValid = false;
                username.classList.add('is-invalid');
                const usernameFeedback = username.closest('.input-group').querySelector('.invalid-feedback');
                if (usernameFeedback) {
                    usernameFeedback.textContent = 'Please enter a valid email address';
                }
            }
            
            // Validate password
            if (!password.value) {
                isValid = false;
                password.classList.add('is-invalid');
                const passwordFeedback = password.closest('.input-group').querySelector('.invalid-feedback');
                if (passwordFeedback) {
                    passwordFeedback.textContent = 'Password is required';
                }
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Show/hide password functionality
    const togglePassword = document.querySelector('.toggle-password');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const passwordField = document.getElementById('password');
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            this.querySelector('i').classList.toggle('bi-eye');
            this.querySelector('i').classList.toggle('bi-eye-slash');
        });
    }
});
