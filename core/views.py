from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
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

    def perform_create(self, serializer):
        # Automatically links the logged-in user as the creator of the team
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
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