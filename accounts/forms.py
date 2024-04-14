from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from wasteman.models import IssueReport


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password')
        labels = {
            'email': 'Email',
            'password': 'Password',
        }
        help_texts = {
            'email': 'Required. Please enter a valid email address.',
        }


class IssueReportForm(forms.ModelForm):
    class Meta:
        model = IssueReport
        exclude = ['status']
        fields = ['issue_type', 'description', ]
        widgets = {
            'issue_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(
                attrs={'class': 'form-control ', 'default': 'Pending', 'disabled': 'disabled', 'required': 'false'}),
        }
