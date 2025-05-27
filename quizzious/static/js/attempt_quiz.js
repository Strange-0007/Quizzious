document.addEventListener('DOMContentLoaded', function() {
    // Timer functionality with localStorage persistence
    const quizId = document.getElementById('quiz-data')?.dataset.quizId;
    const storageKey = `quiz_${quizId}_timer`;
    const totalDuration = parseInt(document.getElementById('quiz-data')?.dataset.duration || "0");
    
    // Check if we have a saved timer value in localStorage
    let timeRemaining;
    const savedTime = localStorage.getItem(storageKey);
    if (savedTime && !isNaN(parseInt(savedTime))) {
        timeRemaining = parseInt(savedTime);
    } else {
        timeRemaining = totalDuration;
    }
    
    const timerElement = document.getElementById('timer');
    
    function updateTimer() {
        if (!timerElement) return;
        
        const hours = Math.floor(timeRemaining / 3600);
        const minutes = Math.floor((timeRemaining % 3600) / 60);
        const seconds = timeRemaining % 60;
        
        timerElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // Save current time to localStorage
        if (timeRemaining > 0) {
            localStorage.setItem(storageKey, timeRemaining.toString());
        }
        
        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            localStorage.removeItem(storageKey); // Clear the timer from storage
            
            // Alert user that time is up
            alert("Time's up! Your quiz will be submitted now.");
            
            const quizForm = document.getElementById('quizForm');
            if (quizForm) quizForm.submit();
        }
        
        // Warning when 1 minute remaining
        if (timeRemaining === 60) {
            alert("Only 1 minute remaining!");
        }
        
        timeRemaining--;
    }
    
    let timerInterval;
    if (timerElement) {
        updateTimer();
        timerInterval = setInterval(updateTimer, 1000);
    }

    // Question navigation functionality
    const quizData = document.getElementById('quiz-data');
    const totalQuestions = quizData ? parseInt(quizData.dataset.questionCount || "0") : 0;
    let currentQuestion = 0;
    const questionElements = document.querySelectorAll('.question-item');
    const progressBar = document.getElementById('progressBar');
    const currentQuestionNum = document.getElementById('currentQuestionNum');
    const questionProgress = document.getElementById('questionProgress');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const submitButton = document.getElementById('submitButton');
    const quizForm = document.getElementById('quizForm');
    
    // Create question navigation indicators
    const createQuestionNavigator = () => {
        const container = document.createElement('div');
        container.className = 'question-navigator d-flex flex-wrap gap-2 mb-3';
        
        for (let i = 0; i < totalQuestions; i++) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-sm btn-outline-secondary question-nav-btn';
            btn.dataset.questionIndex = i;
            btn.textContent = i + 1;
            btn.addEventListener('click', () => {
                currentQuestion = i;
                showQuestion(i);
                updateQuestionNavigator();
            });
            container.appendChild(btn);
        }
        
        const navContainer = document.querySelector('#questionContainer');
        if (navContainer) {
            navContainer.insertBefore(container, navContainer.firstChild);
        }
    };
    
    // Update question navigator to show answered/current questions
    const updateQuestionNavigator = () => {
        const buttons = document.querySelectorAll('.question-nav-btn');
        buttons.forEach((btn, index) => {
            // Reset classes
            btn.classList.remove('btn-primary', 'btn-success', 'btn-outline-secondary');
            
            if (index === currentQuestion) {
                btn.classList.add('btn-primary'); // Current question
            } else if (isQuestionAnswered(index)) {
                btn.classList.add('btn-success'); // Answered question
            } else {
                btn.classList.add('btn-outline-secondary'); // Unanswered question
            }
        });
    };
    
    // Check if a specific question is answered
    function isQuestionAnswered(index) {
        if (!questionElements[index]) return false;
        
        const questionElement = questionElements[index];
        const radioInputs = questionElement.querySelectorAll('input[type="radio"]');
        return Array.from(radioInputs).some(input => input.checked);
    }

    // Function to show current question and update navigation
    function showQuestion(index) {
        if (!questionElements.length) return;
        
        // Hide all questions
        questionElements.forEach(q => q.style.display = 'none');
        
        // Show current question
        if (questionElements[index]) {
            questionElements[index].style.display = 'block';
        }
        
        // Update progress
        if (progressBar) {
            const progress = ((index + 1) / totalQuestions) * 100;
            progressBar.style.width = `${progress}%`;
        }
        
        if (currentQuestionNum) {
            currentQuestionNum.textContent = index + 1;
        }
        
        if (questionProgress) {
            questionProgress.textContent = `${index + 1}/${totalQuestions}`;
        }
        
        // Update buttons
        if (prevButton) {
            prevButton.disabled = index === 0;
        }
        
        if (nextButton && submitButton) {
            if (index === totalQuestions - 1) {
                nextButton.style.display = 'none';
                submitButton.style.display = 'inline-block';
            } else {
                nextButton.style.display = 'inline-block';
                submitButton.style.display = 'none';
            }
        }
        
        // Update navigation indicators
        updateQuestionNavigator();
    }

    // Function to validate if current question has an answer
    function isCurrentQuestionAnswered() {
        return isQuestionAnswered(currentQuestion);
    }

    // Track when a question is answered
    document.querySelectorAll('.question-item input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', () => {
            updateQuestionNavigator();
        });
    });

    // Event listeners for navigation buttons
    if (prevButton) {
        prevButton.addEventListener('click', function() {
            if (currentQuestion > 0) {
                currentQuestion--;
                showQuestion(currentQuestion);
            }
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', function() {
            if (!isCurrentQuestionAnswered()) {
                if (!confirm('You have not answered this question. Continue anyway?')) {
                    return;
                }
            }
            
            if (currentQuestion < totalQuestions - 1) {
                currentQuestion++;
                showQuestion(currentQuestion);
            }
        });
    }

    if (submitButton && quizForm) {
        submitButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (!isCurrentQuestionAnswered()) {
                if (!confirm('You have not answered the current question. Submit quiz anyway?')) {
                    return;
                }
            }
            
            // Check if all questions are answered
            let unansweredCount = 0;
            questionElements.forEach(q => {
                const radioInputs = q.querySelectorAll('input[type="radio"]');
                const answered = Array.from(radioInputs).some(input => input.checked);
                if (!answered) unansweredCount++;
            });
            
            if (unansweredCount > 0) {
                if (!confirm(`You have ${unansweredCount} unanswered question(s). Are you sure you want to submit the quiz?`)) {
                    return;
                }
            }
            
            // Clear timer from localStorage when submitting
            localStorage.removeItem(storageKey);
            
            // Submit the form
            quizForm.submit();
        });
    }

    // Initialize with first question and create navigator
    createQuestionNavigator();
    showQuestion(currentQuestion);
    
    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        // If this is an actual submission, we'll handle cleanup elsewhere
        if (document.activeElement !== submitButton) {
            localStorage.setItem(storageKey, timeRemaining.toString());
        }
    });
});