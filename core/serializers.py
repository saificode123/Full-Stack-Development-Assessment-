from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, Task

class UserSerializer(serializers.ModelSerializer):
    """
    Handles secure user data. 
    Enforces 'No password in plain text' by using create_user for hashing.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        # Security: The password can be written but never read back 
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        # Securely hash password using Django's built-in utility [cite: 31, 42]
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class TeamSerializer(serializers.ModelSerializer):
    """
    Handles Team data. 
    Protects 'creator' field to ensure role-based logic integrity[cite: 14, 45].
    """
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'creator', 'created_at']
        # Security: User cannot spoof the creator; it's set in the view [cite: 40]
        read_only_fields = ['creator', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """
    Handles Task data with nested assignee info for the frontend[cite: 16, 21].
    """
    # Professional touch: Returns username so the UI doesn't have to fetch it separately [cite: 7, 20]
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.username')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'team', 
            'assigned_to', 'assigned_to_name', 'status', 'due_date', 'created_at'
        ]
        # Prevents tampering with auto-generated timestamps [cite: 41]
        read_only_fields = ['created_at']