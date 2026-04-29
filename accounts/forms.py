from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, CareerGoal


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'location', 'linkedin_url', 'github_url', 'website_url', 'career_goal', 'budget_mode', 'learning_style']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/...'}),
            'website_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'career_goal': forms.Select(attrs={'class': 'form-select'}),
            'budget_mode': forms.Select(attrs={'class': 'form-select'}),
            'learning_style': forms.Select(attrs={'class': 'form-select'}),
        }


class CareerGoalSelectionForm(forms.Form):
    career_goal = forms.ModelChoiceField(
        queryset=CareerGoal.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select form-select-lg', 'x-model': 'selectedGoal'}),
        empty_label="Choose your career goal...",
        required=True
    )
    budget_mode = forms.ChoiceField(
        choices=UserProfile.BUDGET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'x-model': 'budgetMode'}),
        required=True
    )
    learning_style = forms.ChoiceField(
        choices=UserProfile.LEARNING_STYLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'x-model': 'learningStyle'}),
        required=True
    )
