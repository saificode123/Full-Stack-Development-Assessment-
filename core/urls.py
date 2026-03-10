from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    TeamViewSet, 
    TaskViewSet,
    UserViewSet # Added to support task assignment dropdown 
)

# 1. Initialize the Router
# This automatically handles /teams/, /tasks/, and the bonus /invite_member/ [cite: 25, 46]
router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'users', UserViewSet, basename='user') # Added for assignment logic [cite: 16, 17]

urlpatterns = [
    # 2. Authentication Routes - Matched perfectly to document requirements [cite: 26, 31]
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # 3. Resource Routes (Teams, Tasks, Users) [cite: 27, 28]
    path('', include(router.urls)),
]