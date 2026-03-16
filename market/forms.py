from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "auth-input"})
        self.fields["password1"].widget.attrs.update({"class": "auth-input"})
        self.fields["password2"].widget.attrs.update({"class": "auth-input"})