from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Post, Category
from django import forms

from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
            }),
            'categoryType': forms.Select(attrs={
                'class': 'form-control',
            }),
            'author': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    postCategory = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')
    password2 = forms.CharField(max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Confirm Password')

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

        def clean(self):
            username = self.cleaned_data.get('username')
            email = self.cleaned_data.get('email')
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Пользователь с таким именем уже существует")
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Пользователь с таким email уже существует")
            return super().clean()


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("username", "password",)


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get_or_create(name='basic')[0]
        basic_group.user_set.add(user)
        return user
