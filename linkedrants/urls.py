from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("translator/", include("translator.urls")),
    path("", include("rants.urls")),
]
