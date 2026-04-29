from django.urls import path
from . import views


urlpatterns = [
    path('', views.community_list, name='community_list'),
    path('create/', views.create_community, name='create_community'),
    path('find-buddies/', views.find_study_buddies, name='find_study_buddies'),
    path('buddy-request/<int:user_id>/', views.send_buddy_request, name='send_buddy_request'),
    path('buddy-respond/<int:match_id>/', views.respond_buddy_request, name='respond_buddy_request'),
    path('<slug:slug>/', views.community_detail, name='community_detail'),
    path('<slug:slug>/join/', views.join_community, name='join_community'),
    path('<slug:slug>/leave/', views.leave_community, name='leave_community'),
    path('<slug:slug>/discuss/', views.create_discussion, name='create_discussion'),
]
