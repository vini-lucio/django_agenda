from typing import Any
from contact.models import Contact
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation


class ContactForm(forms.ModelForm):
    # first_name = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'classe-a classe-b',
    #             'placeholder': 'escreva 3',
    #         }
    #     ),
    #     label='Primeiro Nome',
    #     help_text='texto ajuda'
    # )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    # self.fields['first_name'].widget.attrs.update({'placeholder': 'escreva 2'})

    picture = forms.ImageField(widget=forms.FileInput(attrs={'accept': 'image/*'}), required=False)

    class Meta:
        model = Contact
        fields = 'first_name', 'last_name', 'phone', 'email', 'description', 'category', 'picture'
        # widgets = {
        #     'first_name': forms.TextInput(attrs={
        #         'class': 'classe-a classe-b',
        #         'placeholder': 'escreva'
        #     })
        # }

    def clean(self) -> dict[str, Any]:
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if first_name == last_name:
            msg = ValidationError('primeiro e segundo nome iguais', code='invalid')
            self.add_error('first_name', msg)
            self.add_error('last_name', msg)

        # self.add_error('first_name', ValidationError('teste erro', code='invalid'))
        return super().clean()

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if first_name == 'abc':
            # raise ValidationError('não digite abc', code='invalid')
            self.add_error('first_name', ValidationError('teste erro abc', code='invalid'))

        return first_name


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            self.add_error('email', ValidationError('email repetito', code='invalid'))

        return email


class RegisterUpdateForm(forms.ModelForm):
    first_name = forms.CharField(min_length=2, max_length=30, required=True,
                                 help_text='Required', error_messages={'min_length': 'Min length'})
    last_name = forms.CharField(min_length=2, max_length=30, required=True, help_text='Required')
    password1 = forms.CharField(label='Password', strip=False,
                                widget=forms.PasswordInput(attrs={"autocomplete": "new-password", }),
                                help_text=password_validation.password_validators_help_text_html(), required=False)
    password2 = forms.CharField(label='Password 2', strip=False,
                                widget=forms.PasswordInput(attrs={"autocomplete": "new-password", }),
                                help_text="Mesma senha", required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email

        if current_email != email:
            if User.objects.filter(email=email).exists():
                self.add_error('email', ValidationError('email repetito', code='invalid'))

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as errors:
                self.add_error('password1', ValidationError(errors))

        return password1

    def clean(self) -> dict[str, Any]:
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', 'Senhas diferentes')

        return super().clean()

    def save(self, commit: bool = True) -> Any:
        cleaned_data = self.cleaned_data
        user = super().save(commit=False)
        password = cleaned_data.get('password1')

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user
