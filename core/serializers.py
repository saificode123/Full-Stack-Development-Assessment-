from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        # Security: Ensure the password is never returned in API responses
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        # This built-in method automatically hashes the password securely
        # satisfying the "No password in plain text" requirement.
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        # Security: The user cannot manually set these fields in the request
        read_only_fields = ['creator', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at']