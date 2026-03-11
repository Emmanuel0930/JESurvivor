"""
URL configuration for JESurvivor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from pathlib import Path

from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

FRONTEND_DIR = Path(settings.BASE_DIR) / 'Frontend'


def frontend_index(request):
    return serve(request, 'index.html', document_root=str(FRONTEND_DIR))


def frontend_asset_or_spa(request, requested_path):
    file_path = FRONTEND_DIR / requested_path

    if file_path.is_file():
        return serve(request, requested_path, document_root=str(FRONTEND_DIR))

    # SPA fallback: non-API routes render index.html
    return serve(request, 'index.html', document_root=str(FRONTEND_DIR))


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('blog.Presentation.urls')),
    # Schema extraction
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

print("DEBUG MODE:", settings.DEBUG)

print("Frontend path:", FRONTEND_DIR)

if settings.DEBUG:
    urlpatterns += [
        path('', frontend_index, name='Frontend-index'),
        path('<path:requested_path>', frontend_asset_or_spa, name='Frontend-assets-or-spa'),
    ]

print("URLPATTERNS:", urlpatterns)