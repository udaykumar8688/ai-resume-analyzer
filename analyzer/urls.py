from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('result/<int:pk>/', views.analysis_result, name='analysis_result'),
]
