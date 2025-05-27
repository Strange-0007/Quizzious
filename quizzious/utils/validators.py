import re
from datetime import datetime

class FormValidator:
    """Utility class for form input validation"""
    
    @staticmethod
    def validate_required(value, field_name="Field"):
        """Validates that a field is not empty"""
        if not value or value.strip() == "":
            return False, f"{field_name} is required"
        return True, ""
    
    @staticmethod
    def validate_email(email):
        """Validates email format"""
        if not email or email.strip() == "":
            return False, "Email is required"
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, ""
    
    @staticmethod
    def validate_date(date_str, format="%Y-%m-%d"):
        """Validates date format"""
        if not date_str or date_str.strip() == "":
            return False, "Date is required"
            
        try:
            datetime.strptime(date_str, format)
            return True, ""
        except ValueError:
            return False, f"Invalid date format. Expected format: {format}"
    
    @staticmethod
    def validate_numeric(value, field_name="Number"):
        """Validates numeric input"""
        if not value or value.strip() == "":
            return False, f"{field_name} is required"
            
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, f"{field_name} must be a number"
    
    @staticmethod
    def validate_integer(value, field_name="Number"):
        """Validates integer input"""
        if not value or value.strip() == "":
            return False, f"{field_name} is required"
            
        try:
            int(value)
            return True, ""
        except ValueError:
            return False, f"{field_name} must be an integer"
    
    @staticmethod
    def validate_length(value, min_length=None, max_length=None, field_name="Field"):
        """Validates text length"""
        if not value:
            return False, f"{field_name} is required"
            
        if min_length and len(value) < min_length:
            return False, f"{field_name} must be at least {min_length} characters"
        if max_length and len(value) > max_length:
            return False, f"{field_name} cannot exceed {max_length} characters"
        return True, ""
    
    @staticmethod
    def validate_password(password):
        """Validates password strength"""
        if not password:
            return False, "Password is required"
            
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
            
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
            
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one digit"
            
        return True, ""