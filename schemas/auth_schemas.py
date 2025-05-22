from pydantic import BaseModel, EmailStr, field_validator
import re

class CreateRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Das Passwort muss mindestens 8 Zeichen lang sein.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Das Passwort muss mindestens einen Großbuchstaben enthalten.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Das Passwort muss mindestens einen Kleinbuchstaben enthalten.")
        if not re.search(r"[0-9]", value):
            raise ValueError("Das Passwort muss mindestens eine Zahl enthalten.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Das Passwort muss mindestens ein Sonderzeichen enthalten.")
        return value


class TokenData(BaseModel):
    email: EmailStr
    id: int
