from django.urls import path

from wasteman import views

urlpatterns = [
    path('', views.home, name='home'),
]
