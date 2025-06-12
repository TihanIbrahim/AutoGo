from pydantic import BaseModel, EmailStr, field_validator
import re

class CreateRequest(BaseModel):
    email: EmailStr  # User email, validated as proper email format
    password: str    # User password string

    @field_validator("password")
    def validate_password(cls, value):
        """
        Validate password strength:
        - Minimum length 8
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(value) < 8:
            raise ValueError("Mindestens 8 Zeichen bitte.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Mindestens ein Großbuchstabe fehlt.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Mindestens ein Kleinbuchstabe fehlt.")
        if not re.search(r"[0-9]", value):
            raise ValueError("Mindestens eine Zahl fehlt.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Mindestens ein Sonderzeichen fehlt.")
        return value


class TokenData(BaseModel):
    email: EmailStr  # Email extracted from token
    id: int          # User ID extracted from token
