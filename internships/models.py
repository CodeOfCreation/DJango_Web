from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Internship(models.Model):
    TYPE_CHOICES = [
        ('remote', 'Remote'),
        ('onsite', 'On-site'),
        ('hybrid', 'Hybrid'),
    ]
    
    DURATION_CHOICES = [
        ('1_month', '1 Month'),
        ('2_months', '2 Months'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
    ]
    
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    requirements = models.TextField(help_text="Skills and qualifications required")
    responsibilities = models.TextField(help_text="Key responsibilities")
    location = models.CharField(max_length=200)
    internship_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='remote')
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='3_months')
    stipend = models.CharField(max_length=100, blank=True, help_text="e.g., '$1000/month', 'Unpaid'")
    application_deadline = models.DateField()
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_internships'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def get_absolute_url(self):
        return reverse('internship_detail', kwargs={'slug': self.slug})
    
    @property
    def applications_count(self):
        return self.applications.count()


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='internship_applications'
    )
    resume = models.FileField(upload_to='internships/resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['internship', 'applicant']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} - {self.internship.title}"
