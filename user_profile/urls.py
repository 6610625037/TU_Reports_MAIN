from django.urls import path
from . import views

app_name = 'user_profile'

urlpatterns = [
    path('', views.profile_view, name='view'),
    path('edit/', views.edit_profile, name='edit'),
    path('settings/', views.settings_view, name='settings'),
    path('security/', views.security_settings, name='security'),
]
