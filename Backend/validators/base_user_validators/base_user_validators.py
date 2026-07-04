from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator
import re

username_validator = RegexValidator(regex=r'^[a-zA-Z0-9_]+$',message='Username может содержать только буквы, цифры и подчеркивание')

email_regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"


username_length_validator = MinLengthValidator(8, message='Username должен быть минимум 3 символа')

def validate_username(value):
    unusable_usernames = ['admin', 'root', 'moderator', 'support', 'system']
    if value in unusable_usernames:
        raise ValidationError(f'username "{value}" зарезервирован')

def validate_username_no_spaces(value):
    if ' ' in value:
        raise ValidationError(f'Username не может содержать пробелы')


def validate_email(value):
    if not re.match(email_regex, value):
        raise ValidationError('Некорректный формат email')
