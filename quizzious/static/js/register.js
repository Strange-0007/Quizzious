/**
 * Registration form validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Registration form validation
    const registerForm = document.getElementById('registerForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            let isValid = true;
            const username = document.getElementById('username');
            const fullName = document.getElementById('full_name');
            const qualification = document.getElementById('qualification');
            const dob = document.getElementById('dob');
            const password = document.getElementById('password');
            
            // Reset any previous error messages
            document.querySelectorAll('.invalid-feedback').forEach(el => {
                el.textContent = '';
            });
            document.querySelectorAll('.is-invalid').forEach(el => {
                el.classList.remove('is-invalid');
            });
            
            // Validate username/email
            if (!username.value.trim()) {
                isValid = false;
                username.classList.add('is-invalid');
                username.nextElementSibling.textContent = 'Username is required';
            } else {
                // Check if username is an email
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(username.value)) {
                    isValid = false;
                    username.classList.add('is-invalid');
                    username.nextElementSibling.textContent = 'Please enter a valid email address';
                }
            }
            
            // Validate full name
            if (!fullName.value.trim()) {
                isValid = false;
                fullName.classList.add('is-invalid');
                fullName.nextElementSibling.textContent = 'Full name is required';
            }
            
            // Validate qualification
            if (!qualification.value.trim()) {
                isValid = false;
                qualification.classList.add('is-invalid');
                qualification.nextElementSibling.textContent = 'Qualification is required';
            }
            
            // Validate date of birth
            if (!dob.value) {
                isValid = false;
                dob.classList.add('is-invalid');
                dob.nextElementSibling.textContent = 'Date of birth is required';
            } else {
                // Check if user is at least 12 years old
                const dobDate = new Date(dob.value);
                const today = new Date();
                const minAgeDate = new Date(today.getFullYear() - 12, today.getMonth(), today.getDate());
                
                if (dobDate > minAgeDate) {
                    isValid = false;
                    dob.classList.add('is-invalid');
                    dob.nextElementSibling.textContent = 'You must be at least 12 years old';
                }
            }
            
            // Validate password
            if (!password.value) {
                isValid = false;
                password.classList.add('is-invalid');
                password.nextElementSibling.textContent = 'Password is required';
            } else if (password.value.length < 6) {
                isValid = false;
                password.classList.add('is-invalid');
                password.nextElementSibling.textContent = 'Password must be at least 6 characters long';
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