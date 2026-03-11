from django.contrib import admin
from django.urls import path, include
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
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

# Determine if we're in production (has DATABASE_URL but not DEBUG)
is_production = os.getenv('DATABASE_URL') is not None and os.getenv('DEBUG', 'False') != 'True'

# In production, use /api/ prefix; in development, use root
if is_production:
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('api/debug/db/', debug_db, name='debug_db'),
        path('api/', include('core.urls')), 
    ]
else:
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('debug/db/', debug_db, name='debug_db'),
        path('', include('core.urls')), 
    ]