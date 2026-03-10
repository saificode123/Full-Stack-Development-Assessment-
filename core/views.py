from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserSerializer

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