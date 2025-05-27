// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Get all forms with the class 'needs-validation'
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over each form and prevent submission if validation fails
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Custom email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('input', function() {
            const email = this.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (emailRegex.test(email)) {
                this.setCustomValidity('');
            } else {
                this.setCustomValidity('Please enter a valid email address');
            }
        });
    });
    
    // Password strength validation
    const passwordInputs = document.querySelectorAll('input[type="password"].password-strength');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const password = this.value;
            const minLength = 8;
            
            if (password.length < minLength) {
                this.setCustomValidity(`Password must be at least ${minLength} characters long`);
            } else if (!/[A-Z]/.test(password)) {
                this.setCustomValidity('Password must contain at least one uppercase letter');
            } else if (!/[a-z]/.test(password)) {
                this.setCustomValidity('Password must contain at least one lowercase letter');
            } else if (!/[0-9]/.test(password)) {
                this.setCustomValidity('Password must contain at least one number');
            } else {
                this.setCustomValidity('');
            }
        });
    });
    
    // Confirm password validation
    const confirmPasswordInputs = document.querySelectorAll('input.confirm-password');
    confirmPasswordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const passwordInput = this.form.querySelector('input[type="password"]:not(.confirm-password)');
            if (passwordInput && this.value !== passwordInput.value) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    });
});

// Toggle password visibility
function togglePasswordVisibility(inputId) {
    const passwordInput = document.getElementById(inputId);
    const icon = passwordInput.nextElementSibling.querySelector('i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}

// Tooltips and Popovers initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Quiz timer functionality
function startQuizTimer(durationInMinutes, displayElement) {
    if (!displayElement) return;
    
    let timer = durationInMinutes * 60;
    const display = document.getElementById(displayElement);
    
    const interval = setInterval(function() {
        const minutes = Math.floor(timer / 60);
        const seconds = timer % 60;
        
        display.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        
        if (--timer < 0) {
            clearInterval(interval);
            display.textContent = "Time's up!";
            document.querySelector('form.quiz-form').submit();
        }
    }, 1000);
}

// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', function() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }
});
