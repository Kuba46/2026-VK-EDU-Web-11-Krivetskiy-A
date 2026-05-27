from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from questions.models import Profile


User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput)


class SignupForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='Name', max_length=150, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
            Profile.objects.get_or_create(user=user)
        return user


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(label='Avatar', required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Profile.objects.get_or_create(user=self.instance)

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            return avatar

        max_size_bytes = 2 * 1024 * 1024
        if avatar.size > max_size_bytes:
            raise forms.ValidationError('Avatar size must be 2MB or less.')

        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        ext = avatar.name.rsplit('.', 1)[-1].lower() if '.' in avatar.name else ''
        if f'.{ext}' not in allowed_extensions:
            raise forms.ValidationError('Allowed formats: JPG, PNG, GIF, WEBP.')

        return avatar

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, _ = Profile.objects.get_or_create(user=user)
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            profile.avatar = avatar
            profile.save(update_fields=['avatar'])
        return user
