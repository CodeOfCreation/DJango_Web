from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Job(models.Model):
    TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (2-5 years)'),
        ('senior', 'Senior Level (5+ years)'),
        ('lead', 'Lead/Manager'),
    ]
    
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    requirements = models.TextField(help_text="Skills and qualifications required")
    responsibilities = models.TextField(help_text="Key responsibilities")
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='entry')
    salary_min = models.PositiveIntegerField(blank=True, null=True, help_text="Minimum annual salary in USD")
    salary_max = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum annual salary in USD")
    skills_required = models.CharField(max_length=500, help_text="Comma-separated required skills")
    benefits = models.TextField(blank=True, help_text="Benefits and perks")
    application_deadline = models.DateField()
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def get_absolute_url(self):
        return reverse('job_detail', kwargs={'slug': self.slug})
    
    def get_salary_display(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        elif self.salary_min:
            return f"${self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,}"
        return "Not specified"
    
    @property
    def applications_count(self):
        return self.applications.count()
    
    def get_skills_list(self):
        return [skill.strip() for skill in self.skills_required.split(',') if skill.strip()]


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    resume = models.FileField(upload_to='jobs/resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"
