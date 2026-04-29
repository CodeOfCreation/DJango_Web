from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class CareerGoal(models.Model):
    CATEGORY_CHOICES = [
        ('data_science', 'Data Science'),
        ('web_development', 'Web Development'),
        ('mobile_development', 'Mobile Development'),
        ('cloud_devops', 'Cloud & DevOps'),
        ('cybersecurity', 'Cybersecurity'),
        ('ai_ml', 'AI & Machine Learning'),
        ('game_development', 'Game Development'),
        ('blockchain', 'Blockchain & Web3'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    icon = models.CharField(max_length=50, default='bi-briefcase')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    BUDGET_CHOICES = [
        ('free_only', 'Free Resources Only'),
        ('free_and_paid', 'Best Quality (Free + Paid)'),
    ]
    
    LEARNING_STYLE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('interactive', 'Interactive Labs'),
        ('mixed', 'Mixed'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    career_goal = models.ForeignKey(CareerGoal, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    budget_mode = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='free_and_paid')
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLE_CHOICES, default='mixed')
    location = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    is_mentor = models.BooleanField(default=False)
    mentor_bio = models.TextField(max_length=500, blank=True)
    is_employer = models.BooleanField(default=False)
    company_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def completion_percentage(self):
        """Calculate overall roadmap completion percentage"""
        from roadmaps.models import UserProgress
        total_topics = UserProgress.objects.filter(user=self.user).count()
        if total_topics == 0:
            return 0
        completed_topics = UserProgress.objects.filter(user=self.user, is_completed=True).count()
        return round((completed_topics / total_topics) * 100, 1)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
