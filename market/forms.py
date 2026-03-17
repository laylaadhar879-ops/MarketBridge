from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email", "password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["first_name"].widget.attrs.update({"class": "auth-input"})
        self.fields["last_name"].widget.attrs.update({"class": "auth-input"})
        self.fields["email"].widget.attrs.update({"class": "auth-input"})
        self.fields["password"].widget.attrs.update({"class": "auth-input"})

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"]
        user.email = email
        user.username = email
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
