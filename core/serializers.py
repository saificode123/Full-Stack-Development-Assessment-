from rest_framework import serializers
from django.contrib.auth.models import User

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