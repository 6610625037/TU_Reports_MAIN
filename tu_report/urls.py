"""
URL configuration for tu_report project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),  # Redirect to main dashboard
    path('', include('authentication.urls')),
    path('tickets/', include('tickets.urls')),
    path('technician/', include('technician.urls')),
    path('dashboard/', include('dashboard.urls')),  # Main dashboard is now /dashboard/ (was /dashboard/map/)
    path('notifications/', include('notify.urls')),
    path('reports/', include('reports.urls')),
    path('profile/', include('user_profile.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
