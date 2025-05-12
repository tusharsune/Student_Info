from django import forms
from django.contrib.auth.models import User
from .models import Performance, Attendance
import re

# --- Custom User Creation Form ---
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")

            if len(password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")

            if not password1[0].isupper():
                raise forms.ValidationError("Password must start with a capital letter.")

            if not re.search(r'\d', password1):
                raise forms.ValidationError("Password must contain at least one number.")

            if not re.search(r'[A-Z]', password1):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")

            if not re.search(r'[a-z]', password1):
                raise forms.ValidationError("Password must contain at least one lowercase letter.")

            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
                raise forms.ValidationError("Password must contain at least one special character.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
