from django.urls import path

from wasteman import views

urlpatterns = [
    path('', views.home, name='home'),
    path('issue-reports/', views.issue_reports, name='issue_reports'),
    path('update_status/<int:collection_status_id>/', views.update_status, name='update_status'),
]
