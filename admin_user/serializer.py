from rest_framework import serializers
from users.models import User

class AdminUserListSerializer(serializers.ModelSerializer):
    orders_count = serializers.IntegerField(read_only=True)
    cart_items_count = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    last_order = serializers.DateTimeField(read_only=True)
    class Meta:
        model=User
        fields=['id', 'username', 'email', 'phone', 'role', 'blocked', 'date_joined',
                "orders_count", "cart_items_count", "total_spent", "last_order"]
