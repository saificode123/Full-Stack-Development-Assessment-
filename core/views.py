from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

# Local imports
from .models import Team, Task
from .serializers import UserSerializer, TeamSerializer, TaskSerializer
from .permissions import IsTeamCreatorOrReadOnly  


# ==========================================
# AUTHENTICATION VIEWS
# ==========================================

@method_decorator(ensure_csrf_cookie, name='dispatch')
class RegisterView(APIView):
    """
    Handles secure user registration.
    Accessible to anyone (AllowAny).
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():  
            serializer.save()
            return Response({'success': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    """
    Handles user login using Django's session authentication.
    Stores session securely via HTTP-only cookies.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Authenticate checks the hashed password securely
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Creates the session in PostgreSQL and sets the HTTP-only cookie
            login(request, user)
            return Response(
                {'success': 'Logged in successfully', 'username': user.username}, 
                status=status.HTTP_200_OK
            )
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Handles user logout by destroying the session.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        logout(request)
        return Response({'success': 'Logged out successfully'}, status=status.HTTP_200_OK)


# ==========================================
# API ENDPOINTS 
# ==========================================

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint to list users.
    Required for the frontend 'Assign To' dropdown in the Task Modal.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class TeamViewSet(viewsets.ModelViewSet):
    """
    CRUD routes for Teams. 
    Protects delete operations using Role-Based Access Control (RBAC).
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    
    # Restricts access: Must be logged in, and only creators can update/delete
    permission_classes = [permissions.IsAuthenticated, IsTeamCreatorOrReadOnly] 

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs) 

    def perform_create(self, serializer):
        # Automatically links the logged-in user as the creator of the team
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsTeamCreatorOrReadOnly])
    def invite_member(self, request, pk=None):
        """
        Bonus Feature: Stubbed email invite logic.
        Endpoint: POST /teams/{id}/invite_member/
        """
        team = self.get_object()
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required to send an invite."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Stubbed logic: We pretend to send an email here (no SMTP needed) 
        print(f"[STUB] Sending invite email to '{email}' for team '{team.name}'...")
        
        return Response(
            {"success": f"Invite successfully sent to {email}."}, 
            status=status.HTTP_200_OK
        )


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD routes for Tasks.
    Includes robust filtering logic for the frontend dashboard.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated] # Protects non-auth routes 

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """
        Optionally restricts the returned tasks,
        by filtering against 'team' or 'assigned_to' query parameters.
        """
        queryset = Task.objects.all()
        team_id = self.request.query_params.get('team', None)
        assignee_id = self.request.query_params.get('assigned_to', None)
        
        if team_id is not None:
            queryset = queryset.filter(team_id=team_id)
            
        if assignee_id is not None:
            queryset = queryset.filter(assigned_to_id=assignee_id)
            
        return queryset


# ==========================================
# SETTINGS VIEWS
# ==========================================

class ProfileView(APIView):
    """
    GET: Returns the current user's profile (username, email).
    PATCH: Updates the current user's display name (first_name) and email.
    """
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

    def patch(self, request):
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        return Response({
            'success': 'Profile updated successfully.',
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })


class ChangePasswordView(APIView):
    """
    POST: Changes the current user's password.
    Requires current_password and new_password in the request body.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'error': 'Both current_password and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 8:
            return Response(
                {'error': 'New password must be at least 8 characters long.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        # Keep the user logged in after password change
        update_session_auth_hash(request, user)
        return Response({'success': 'Password changed successfully.'})