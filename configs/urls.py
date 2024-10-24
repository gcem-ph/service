"""
URL configuration for service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
import app.urls
from configs import settings
import app

urlpatterns = [
    path(settings.SCRIPT_NAME + 'admin/', admin.site.urls),
    path(settings.SCRIPT_NAME, include(app.urls)),
    path(settings.SCRIPT_NAME + "ckeditor5/", include('django_ckeditor_5.urls')),
    path(settings.SCRIPT_NAME + 'accounts/', include('django.contrib.auth.urls')),
]

urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)