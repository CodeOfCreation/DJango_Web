from django.contrib import admin
from .models import Roadmap, Topic, Resource, UserProgress


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1
    fields = ['title', 'url', 'resource_type', 'price', 'platform', 'is_verified']


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    fields = ['title', 'order', 'estimated_time', 'domain', 'is_milestone']
    show_change_link = True


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ['title', 'career_goal', 'difficulty', 'estimated_duration', 'is_published', 'created_at']
    list_filter = ['career_goal', 'difficulty', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TopicInline]
    raw_id_fields = ['career_goal', 'created_by']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'roadmap', 'order', 'domain', 'estimated_time', 'is_milestone']
    list_filter = ['domain', 'is_milestone', 'roadmap__career_goal']
    search_fields = ['title', 'description']
    inlines = [ResourceInline]
    filter_horizontal = ['prerequisites']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'resource_type', 'platform', 'price', 'is_verified', 'created_at']
    list_filter = ['resource_type', 'platform', 'is_verified', 'created_at']
    search_fields = ['title', 'description', 'url']
    raw_id_fields = ['topic']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'is_completed', 'completed_at', 'updated_at']
    list_filter = ['is_completed', 'updated_at']
    search_fields = ['user__username', 'topic__title', 'notes']
    raw_id_fields = ['user', 'topic']
