from django.urls import path
from . import views


urlpatterns = [
    path('', views.explore_roadmaps, name='explore_roadmaps'),
    path('create/', views.create_roadmap, name='create_roadmap'),
    path('progress/', views.my_progress, name='my_progress'),
    path('topic/<int:topic_id>/complete/', views.mark_topic_complete, name='mark_topic_complete'),
    path('<slug:slug>/', views.roadmap_detail, name='roadmap_detail'),
]
