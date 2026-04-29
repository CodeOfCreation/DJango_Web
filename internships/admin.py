from django.contrib import admin
from .models import Internship, Application


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'internship_type', 'duration', 'is_active', 'application_deadline', 'created_at']
    list_filter = ['internship_type', 'duration', 'is_active', 'created_at']
    search_fields = ['title', 'company', 'description', 'requirements']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['posted_by']
    date_hierarchy = 'created_at'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'internship', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['applicant__username', 'internship__title']
    raw_id_fields = ['applicant', 'internship']
