from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('analytics/export/', views.export_report, name='export'),
    path('analytics/heatmap/', views.heatmap_data, name='heatmap'),
]
