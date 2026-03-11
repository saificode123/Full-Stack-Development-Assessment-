from django.contrib import admin
from django.urls import path, include
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os

@csrf_exempt
@api_view(['GET'])
def debug_db(request):
    """Debug endpoint to check database connection"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        # Get table count
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
        
        return Response({
            'status': 'connected',
            'db_test': result,
            'tables': tables,
            'database': connection.settings_dict.get('NAME', 'unknown')
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def api_root(request):
    """API root endpoint - returns API info"""
    return JsonResponse({
        'status': 'running',
        'message': 'Team Task Manager API',
        'endpoints': {
            'auth': '/auth/',
            'teams': '/teams/',
            'tasks': '/tasks/',
            'users': '/users/',
            'profile': '/auth/profile/',
        },
        'docs': '/admin/'
    })

# URL configuration - support both /api/ prefix and root level URLs
# This ensures compatibility with different frontend configurations
urlpatterns = [
    path('admin/', admin.site.urls),
    path('debug/db/', debug_db, name='debug_db'),
    
    # Root URL - must come BEFORE include to catch exact /
    path('', api_root, name='api_root'),
    
    # Include core URLs at root level (for production frontend)
    path('', include('core.urls')),
    
    # Also include at /api/ prefix (for consistency)
    path('api/', include('core.urls')),
]

# Serve static files in production
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
