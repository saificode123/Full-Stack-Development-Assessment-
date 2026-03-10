from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include core.urls at the root so /auth, /teams, and /tasks work directly
    path('', include('core.urls')), 
]