from django.urls import path
from . import views


urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('post/', views.post_job, name='post_job'),
    path('my-applications/', views.my_job_applications, name='my_job_applications'),
    path('<slug:slug>/', views.job_detail, name='job_detail'),
    path('<slug:slug>/apply/', views.apply_job, name='apply_job'),
]
