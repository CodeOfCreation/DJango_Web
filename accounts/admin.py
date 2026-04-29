from django.contrib import admin
from .models import CareerGoal, UserProfile


@admin.register(CareerGoal)
class CareerGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'career_goal', 'budget_mode', 'learning_style', 'created_at']
    list_filter = ['budget_mode', 'learning_style', 'is_mentor', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    raw_id_fields = ['user', 'career_goal']
