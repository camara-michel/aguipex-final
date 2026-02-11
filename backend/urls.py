"""
URL configuration for backend project.
Site web AGUIPEX uniquement.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include("core.urls")),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    # Only serve media files locally if MEDIA_URL is a relative path
    if settings.MEDIA_URL.startswith('/'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files from STATICFILES_DIRS in development
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
else:
    # In production, static files should be served by the web server
    # Only serve media files if MEDIA_URL is a relative path
    if settings.MEDIA_URL.startswith('/'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
