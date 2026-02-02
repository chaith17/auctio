# auctions/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Auction, UserProfile, Vendue

class VendueForm(forms.ModelForm):
    class Meta:
        model = Vendue
        fields = ['title', 'description', 'base_price', 'duration_minutes', 'category', 'attachment']
        widgets = {
            'description': forms.Textarea(attrs={'rows':4, 'class': 'glass-input h-28', 'placeholder': 'Describe your item (condition, history, special notes...)'}),
            'title': forms.TextInput(attrs={'class': 'glass-input', 'placeholder': 'Title of your auction', 'id': 'id_title'}),
            'base_price': forms.NumberInput(attrs={'class': 'glass-input', 'placeholder': 'Base Price', 'id': 'id_base_price'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'glass-input', 'placeholder': '60', 'id': 'id_duration_minutes'}),
            'category': forms.Select(attrs={'class': 'glass-input glass-select', 'id': 'id_category'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'glass-input', 'id': 'id_attachment', 'accept': 'image/*'}),
        }
        labels = {
            "base_price": "Base Price",
            "attachment": "Attachment",
        }

class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={"class": "glass-input", "placeholder": "Username", "id": "id_username"}
    ))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={"class": "glass-input", "placeholder": "Email", "id": "id_email"}
    ))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(
        attrs={"class": "glass-input", "placeholder": "Password", "id": "id_password1"}
    ))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(
        attrs={"class": "glass-input", "placeholder": "Confirm Password", "id": "id_password2"}
    ))
    avatar = forms.ImageField(required=False, widget=forms.ClearableFileInput(
        attrs={"class": "glass-input custom-file-input", "id": "id_avatar"}
    ))

    class Meta:
        model = UserProfile
        fields = ("username", "email", "password1", "password2", "avatar")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
