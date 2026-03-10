from django.contrib.auth import authenticate, login, logout
from .permissions import IsCreatorOrReadOnly
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Team, Task
from .serializers import UserSerializer, TeamSerializer, TaskSerializer
from rest_framework import viewsets

class RegisterView(APIView):
    # Allow anyone to access the registration route
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(): # Triggers the input validation
            serializer.save()
            return Response({'success': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Authenticate checks the hashed password securely
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # This creates the session in PostgreSQL and sets the HTTP-only cookie
            login(request, user)
            return Response({'success': 'Logged in successfully', 'username': user.username}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'success': 'Logged out successfully'}, status=status.HTTP_200_OK)
    

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    # Added IsCreatorOrReadOnly to satisfy the bonus requirement
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly] 

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    # Bonus: Stubbed email invite logic
    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Stubbed logic: We pretend to send an email here
        print(f"STUB: Sending invite email to {email} for team {self.get_object().name}")
        return Response({"success": f"Invite sent to {email}"}, status=status.HTTP_200_OK)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Added filtering logic to satisfy the frontend requirement
    def get_queryset(self):
        queryset = Task.objects.all()
        team_id = self.request.query_params.get('team', None)
        assignee_id = self.request.query_params.get('assigned_to', None)
        
        if team_id is not None:
            queryset = queryset.filter(team_id=team_id)
        if assignee_id is not None:
            queryset = queryset.filter(assigned_to_id=assignee_id)
            
        return queryset