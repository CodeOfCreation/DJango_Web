from django import forms
from .models import Internship, Application


class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ['title', 'company', 'description', 'requirements', 'responsibilities', 
                  'location', 'internship_type', 'duration', 'stipend', 
                  'application_deadline']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Required skills and qualifications'}),
            'responsibilities': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Key responsibilities'}),
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
            'stipend': forms.TextInput(attrs={'placeholder': 'e.g., $1000/month or Unpaid'}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Why are you interested in this internship?'}),
        }
