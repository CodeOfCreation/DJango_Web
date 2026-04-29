from django import forms
from .models import Article, Category


class ArticleForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=200,
        required=False,
        help_text="Comma-separated tags",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., python, django, web development'})
    )
    
    class Meta:
        model = Article
        fields = ['title', 'category', 'content', 'excerpt', 'thumbnail', 'difficulty', 'tags', 'featured']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 15, 'placeholder': 'Write your article content here...'}),
            'excerpt': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief summary of the article'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select a category"
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
