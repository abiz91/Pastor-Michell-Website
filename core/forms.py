from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import MemberProfile

User = get_user_model()


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "First name",
            "autocomplete": "given-name",
        }),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Last name",
            "autocomplete": "family-name",
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )
    phone_number = forms.CharField(
        max_length=30,
        widget=forms.TelInput(attrs={
            "placeholder": "+234 800 000 0000",
            "autocomplete": "tel",
        }),
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Country"}),
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "placeholder": "City",
            "autocomplete": "address-level2",
        }),
    )
    gender = forms.ChoiceField(
        choices=MemberProfile.GENDER_CHOICES,
        widget=forms.Select(),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "country",
            "city",
            "gender",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = (
            "Used to sign in. You can use your email as your username if you prefer."
        )
        self.fields["username"].widget.attrs.update({
            "placeholder": "Choose a username",
            "autocomplete": "username",
        })
        self.fields["password1"].widget.attrs.update({
            "autocomplete": "new-password",
            "placeholder": "Create a strong password",
        })
        self.fields["password2"].widget.attrs.update({
            "autocomplete": "new-password",
            "placeholder": "Repeat your password",
        })

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.email = self.cleaned_data["email"].strip().lower()

        if commit:
            user.save()
            MemberProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data["phone_number"].strip(),
                country=self.cleaned_data["country"].strip(),
                city=self.cleaned_data["city"].strip(),
                gender=self.cleaned_data["gender"],
            )

        return user
