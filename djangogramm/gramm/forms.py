from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm,
    AuthenticationForm as DjangoAuthenticationForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from taggit.models import Tag

from gramm.models import Post
from gramm.utils import send_email_for_verify

User = get_user_model()


class LoginUserForm(DjangoAuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

            if not self.user_cache.email_verify:
                send_email_for_verify(self.request, self.user_cache)
                raise ValidationError(
                    'Email not verified , check your email',
                    code='invalid_login',
                )

        return self.cleaned_data


class UserRegistrationForm(DjangoUserCreationForm):
    email = forms.EmailField(
        label=_('Email'),
        max_length=250,
        widget=forms.TextInput(attrs={'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'placeholder':
                                              'Password'})
    )

    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    avatar = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea)


class CreatePostForm(forms.ModelForm):
    tags_objects = Tag.objects.all()
    tags2 = forms.ModelMultipleChoiceField(
        required=False,
        queryset=tags_objects,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Tags',
    )
    image1 = forms.ImageField(widget=forms.ClearableFileInput(), required=True)
    image2 = forms.ImageField(widget=forms.ClearableFileInput(), required=False)
    image3 = forms.ImageField(widget=forms.ClearableFileInput(), required=False)

    class Meta:
        model = Post
        fields = ['tags', 'tags2', 'image1', 'image2', 'image3']
        labels = {'tags': 'Add new tag(s)'}

class LikeForm(forms.Form):
    post_id = forms.IntegerField(widget=forms.HiddenInput())

class FollowForm(forms.Form):
    author_id = forms.IntegerField(widget=forms.HiddenInput())
