from django import forms
from .models import Community, Discussion


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'category', 'roadmap', 'icon', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the purpose and goals of this community'}),
            'icon': forms.TextInput(attrs={'placeholder': 'e.g., bi-people, bi-laptop, bi-rocket'}),
        }
        help_texts = {
            'icon': 'Use Bootstrap Icons class names (e.g., bi-people)',
            'roadmap': 'Optional: Link this community to a specific learning roadmap',
        }


class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Start a discussion...'}),
        }
