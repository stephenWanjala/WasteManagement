from django.urls import path

from wasteman import views

urlpatterns = [
    path('', views.home, name='home'),
    path('issue-reports/', views.issue_reports, name='issue_reports'),
]
