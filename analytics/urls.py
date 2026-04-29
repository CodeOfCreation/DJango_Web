from django.urls import path
from . import views


urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('api/progress/', views.progress_data_api, name='progress_data_api'),
    path('api/skills/', views.skill_data_api, name='skill_data_api'),
    path('api/stats/', views.overall_stats_api, name='overall_stats_api'),
]
