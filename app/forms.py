from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from .models import UserProfile, Message, UserRole


class UserRegistrationForm(forms.ModelForm):
    """User registration form"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        label='Confirm Password'
    )
    role = forms.ChoiceField(
        choices=UserRole.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='User Role'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one digit.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError('Passwords do not match.')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """User login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Remember me'
    )


class SendMessageForm(forms.ModelForm):
    """Form to send a message"""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Enter your message content here...'
        }),
        label='Message Content'
    )

    class Meta:
        model = Message
        fields = ('receiver', 'subject')
        widgets = {
            'receiver': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Message Subject'
            }),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active users as receivers (exclude current user)
        if current_user:
            self.fields['receiver'].queryset = User.objects.filter(
                is_active=True
            ).exclude(id=current_user.id)
        else:
            self.fields['receiver'].queryset = User.objects.filter(is_active=True)


class CAApprovalForm(forms.Form):
    """Form for Cloud Authority to approve messages"""
    certificate_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter certificate/signature data'
        }),
        label='Certificate/Signature'
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes'
        }),
        required=False,
        label='Notes'
    )

    class Meta:
        pass


class MessageFilterForm(forms.Form):
    """Form to filter messages"""
    STATUS_CHOICES = [
        ('', 'All Statuses'),
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ROUTER_ACCEPTED', 'Router Accepted'),
        ('CERTIFICATE_CREATED', 'Certificate Created'),
        ('DELIVERED', 'Delivered'),
        ('REJECTED', 'Rejected'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sender = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by sender'
        })
    )
    date_from = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
