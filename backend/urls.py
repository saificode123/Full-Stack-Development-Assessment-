from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # This perfectly matches the document's /auth Register/Login requirement
    path('auth/', include('core.urls')), 
]