from django.urls import path
from . import views


urlpatterns = [
    path('', views.internship_list, name='internship_list'),
    path('post/', views.post_internship, name='post_internship'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('<slug:slug>/', views.internship_detail, name='internship_detail'),
    path('<slug:slug>/apply/', views.apply_internship, name='apply_internship'),
]
