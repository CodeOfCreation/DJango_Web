from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Roadmap(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    career_goal = models.ForeignKey(
        'accounts.CareerGoal',
        on_delete=models.CASCADE,
        related_name='roadmaps'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    estimated_duration = models.CharField(max_length=50, help_text="e.g., '6 months', '12 weeks'")
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_roadmaps'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['career_goal', 'difficulty', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.career_goal.name})"
    
    def get_absolute_url(self):
        return reverse('roadmap_detail', kwargs={'slug': self.slug})
    
    @property
    def topic_count(self):
        return self.topics.count()
    
    @property
    def total_estimated_hours(self):
        # Parse estimated duration to hours (rough estimate)
        duration = self.estimated_duration.lower()
        if 'month' in duration:
            try:
                months = int(''.join(filter(str.isdigit, duration)))
                return months * 4 * 40  # 40 hours per week, 4 weeks per month
            except ValueError:
                return 0
        elif 'week' in duration:
            try:
                weeks = int(''.join(filter(str.isdigit, duration)))
                return weeks * 40
            except ValueError:
                return 0
        return 0


class Topic(models.Model):
    DOMAIN_CHOICES = [
        ('math', 'Mathematics'),
        ('coding', 'Coding'),
        ('stats', 'Statistics'),
        ('tools', 'Tools & Frameworks'),
        ('theory', 'Theory & Concepts'),
        ('practical', 'Practical Application'),
        ('soft_skills', 'Soft Skills'),
        ('domain_knowledge', 'Domain Knowledge'),
    ]
    
    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.CASCADE,
        related_name='topics'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    estimated_time = models.CharField(max_length=50, help_text="e.g., '2 weeks', '40 hours'")
    estimated_hours = models.PositiveIntegerField(default=10, help_text="Estimated hours to complete this topic")
    domain = models.CharField(max_length=50, choices=DOMAIN_CHOICES, default='coding')

    is_milestone = models.BooleanField(default=False, help_text="Major milestone topic")
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='required_for'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.order}. {self.title}"
    
    @property
    def free_resources_count(self):
        return self.resources.filter(resource_type='free').count()
    
    @property
    def paid_resources_count(self):
        return self.resources.filter(resource_type='paid').count()


class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('free', '🟢 Free'),
        ('paid', '🔵 Paid'),
    ]
    
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('coursera', 'Coursera'),
        ('udemy', 'Udemy'),
        ('kaggle', 'Kaggle'),
        ('github', 'GitHub'),
        ('medium', 'Medium'),
        ('freecodecamp', 'freeCodeCamp'),
        ('docs', 'Official Documentation'),
        ('book', 'Book'),
        ('article', 'Article'),
        ('interactive', 'Interactive Platform'),
        ('other', 'Other'),
    ]
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField()
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price in USD")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='other')
    is_verified = models.BooleanField(default=False, help_text="Verified high-quality resource")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['resource_type', 'platform', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


class UserProgress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='topic_progress'
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Personal notes about this topic")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'topic']
        ordering = ['-updated_at']
    
    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.user.username} - {self.topic.title} ({status})"
