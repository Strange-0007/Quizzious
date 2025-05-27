from utils.validators import FormValidator

class FormHandler:
    """Handler class for form validation and processing"""
    
    def __init__(self):
        self.validator = FormValidator()
        self.errors = {}
    
    def validate_user_form(self, form_data):
        """Validates user creation/edit form"""
        self.errors = {}
        
        # Validate username (email)
        is_valid, message = self.validator.validate_email(form_data.get('username', ''))
        if not is_valid:
            self.errors['username'] = message
        
        # Validate full name
        is_valid, message = self.validator.validate_required(form_data.get('full_name', ''), "Full name")
        if not is_valid:
            self.errors['full_name'] = message
        
        # Validate date of birth
        is_valid, message = self.validator.validate_date(form_data.get('dob', ''))
        if not is_valid:
            self.errors['dob'] = message
            
        # Validate password if present (for new users or password changes)
        if 'password' in form_data and form_data.get('password'):
            is_valid, message = self.validator.validate_password(form_data.get('password', ''))
            if not is_valid:
                self.errors['password'] = message
        
        return len(self.errors) == 0
    
    def validate_subject_form(self, form_data):
        """Validates subject creation/edit form"""
        self.errors = {}
        
        # Validate name
        is_valid, message = self.validator.validate_required(form_data.get('name', ''), "Subject name")
        if not is_valid:
            self.errors['name'] = message
            
        # Validate description length
        is_valid, message = self.validator.validate_length(
            form_data.get('description', ''), 
            min_length=10, 
            max_length=500, 
            field_name="Description"
        )
        if not is_valid:
            self.errors['description'] = message
        
        return len(self.errors) == 0
    
    def validate_chapter_form(self, form_data):
        """Validates chapter creation/edit form"""
        self.errors = {}
        
        # Validate name
        is_valid, message = self.validator.validate_required(form_data.get('name', ''), "Chapter name")
        if not is_valid:
            self.errors['name'] = message
            
        # Validate subject_id
        is_valid, message = self.validator.validate_integer(form_data.get('subject_id', ''), "Subject ID")
        if not is_valid:
            self.errors['subject_id'] = message
        
        # Validate description length
        if 'description' in form_data:
            is_valid, message = self.validator.validate_length(
                form_data.get('description', ''), 
                max_length=500, 
                field_name="Description"
            )
            if not is_valid:
                self.errors['description'] = message
        
        return len(self.errors) == 0
    
    def validate_quiz_form(self, form_data):
        """Validates quiz creation/edit form"""
        self.errors = {}
        
        # Validate quiz name
        is_valid, message = self.validator.validate_required(form_data.get('quiz_name', ''), "Quiz name")
        if not is_valid:
            self.errors['quiz_name'] = message
        
        # Validate chapter_id
        is_valid, message = self.validator.validate_integer(form_data.get('chapter_id', ''), "Chapter ID")
        if not is_valid:
            self.errors['chapter_id'] = message
        
        # Validate date
        is_valid, message = self.validator.validate_date(form_data.get('date_of_quiz', ''))
        if not is_valid:
            self.errors['date_of_quiz'] = message
        
        # Validate time duration
        is_valid, message = self.validator.validate_numeric(form_data.get('time_duration', ''), "Time duration")
        if not is_valid:
            self.errors['time_duration'] = message
        
        return len(self.errors) == 0
    
    def validate_question_form(self, form_data):
        """Validates question creation/edit form"""
        self.errors = {}
        
        # Validate quiz_id
        is_valid, message = self.validator.validate_integer(form_data.get('quiz_id', ''), "Quiz ID")
        if not is_valid:
            self.errors['quiz_id'] = message
        
        # Validate question statement
        is_valid, message = self.validator.validate_required(form_data.get('question_statement', ''), "Question")
        if not is_valid:
            self.errors['question_statement'] = message
        
        # Validate options
        for i in range(1, 5):
            field_name = f'option{i}'
            is_valid, message = self.validator.validate_required(form_data.get(field_name, ''), f"Option {i}")
            if not is_valid:
                self.errors[field_name] = message
        
        # Validate correct option
        is_valid, message = self.validator.validate_integer(form_data.get('correct_option', ''), "Correct option")
        if not is_valid:
            self.errors['correct_option'] = message
        elif int(form_data.get('correct_option', 0)) < 1 or int(form_data.get('correct_option', 0)) > 4:
            self.errors['correct_option'] = "Correct option must be between 1 and 4"
        
        return len(self.errors) == 0