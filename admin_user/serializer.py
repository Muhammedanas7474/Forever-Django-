from rest_framework import serializers
from users.models import User

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id', 'username', 'email', 'phone', 'role', 'blocked', 'date_joined']
