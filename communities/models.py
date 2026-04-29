from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from roadmaps.models import Roadmap, Topic


class Community(models.Model):
    CATEGORY_CHOICES = [
        ('study', 'Study Group'),
        ('career', 'Career Discussion'),
        ('project', 'Project Collaboration'),
        ('general', 'General'),
    ]
    
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    icon = models.CharField(max_length=50, default='bi-people')
    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='communities',
        help_text="Associated roadmap for study groups"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_communities'
    )
    members = models.ManyToManyField(
        User,
        through='Membership',
        related_name='communities'
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Communities'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('community_detail', kwargs={'slug': self.slug})
    
    @property
    def members_count(self):
        return self.members.count()
    
    def is_member(self, user):
        """Check if user is a member of this community"""
        return self.members.filter(id=user.id).exists()


class Membership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'community']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} in {self.community.name}"


class StudyBuddyMatch(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='study_buddy_requests_sent'
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='study_buddy_requests_received'
    )
    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.CASCADE,
        related_name='study_matches'
    )
    current_topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Optional introduction message")
    matched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user1', 'user2', 'roadmap']
        ordering = ['-matched_at']
    
    def __str__(self):
        return f"{self.user1.username} & {self.user2.username} - {self.roadmap.title}"


class Discussion(models.Model):
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='discussions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='discussions'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title
