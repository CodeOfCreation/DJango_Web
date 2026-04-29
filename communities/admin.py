from django.contrib import admin
from .models import Community, Membership, StudyBuddyMatch, Discussion


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_by', 'members_count', 'is_public', 'created_at']
    list_filter = ['category', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['created_by', 'roadmap']
    filter_horizontal = ['members']
    
    def members_count(self, obj):
        return obj.members_count


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'community', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'community__name']
    raw_id_fields = ['user', 'community']


@admin.register(StudyBuddyMatch)
class StudyBuddyMatchAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'roadmap', 'status', 'matched_at']
    list_filter = ['status', 'matched_at']
    search_fields = ['user1__username', 'user2__username', 'roadmap__title']
    raw_id_fields = ['user1', 'user2', 'roadmap', 'current_topic']


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['title', 'community', 'author', 'is_pinned', 'created_at']
    list_filter = ['is_pinned', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    raw_id_fields = ['community', 'author']
