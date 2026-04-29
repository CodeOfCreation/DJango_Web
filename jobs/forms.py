from django import forms
from .models import Job, JobApplication


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'description', 'requirements', 'responsibilities',
                  'location', 'job_type', 'experience_level', 'salary_min', 'salary_max',
                  'skills_required', 'benefits', 'application_deadline']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'rows': 4}),
            'benefits': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Benefits and perks'}),
            'skills_required': forms.TextInput(attrs={'placeholder': 'e.g., Python, Django, JavaScript'}),
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
            'salary_min': forms.NumberInput(attrs={'placeholder': 'Minimum annual salary'}),
            'salary_max': forms.NumberInput(attrs={'placeholder': 'Maximum annual salary'}),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter', 'portfolio_url']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Why are you a good fit for this role?'}),
            'portfolio_url': forms.URLInput(attrs={'placeholder': 'https://your-portfolio.com'}),
        }
