from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class CreateUserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', "last_name", 'email', 'phone_number', 'password1', 'password2,is_resident,'
                                                                                   'is_collector')
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': 'Phone Number',
        }
        help_texts = {
            'email': 'Required. Please enter a valid email address.',
        }


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
