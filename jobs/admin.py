from django.contrib import admin
from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'job_type', 'experience_level', 'is_active', 'application_deadline', 'created_at']
    list_filter = ['job_type', 'experience_level', 'is_active', 'created_at']
    search_fields = ['title', 'company', 'description', 'requirements', 'skills_required']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['posted_by']
    date_hierarchy = 'created_at'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['applicant__username', 'job__title']
    raw_id_fields = ['applicant', 'job']
