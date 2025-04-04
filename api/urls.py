from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register),
    path('password-reset/', views.password_reset_request,name="password_reset_request"),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]