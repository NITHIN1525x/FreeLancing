from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('jobs.urls')),
    path('api/', include('proposals.urls')),
    path('api/', include('projects.urls')),
    path('api/', include('chat.urls')),
    path('api/', include('disputes.urls')),
]

# In production Nginx/S3 serves media; this helper is for local development only.
if settings.DEBUG and not settings.USE_S3_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
