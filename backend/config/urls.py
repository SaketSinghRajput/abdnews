"""
URL configuration for NewsHub backend.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/', include('apps.core.urls')),
    path('api/news/', include('apps.news.urls')),
    path('api/users/', include('apps.users.urls')),
    
    # Redirect /articles/ to /api/news/articles/
    path('articles/', RedirectView.as_view(url='/api/news/articles/', permanent=False)),

    # Frontend routes (served by Django)
    path('', TemplateView.as_view(template_name='index.html'), name='frontend-home'),
    path('', TemplateView.as_view(template_name='index.html')),
    path('pages/<path:path>', serve, {'document_root': settings.FRONTEND_DIR / 'pages'}),
    path('components/<path:path>', serve, {'document_root': settings.FRONTEND_DIR / 'components'}),
    path('assets/<path:path>', serve, {'document_root': settings.FRONTEND_DIR / 'assets'}),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
