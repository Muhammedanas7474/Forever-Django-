from rest_framework import serializers
from order.models import Order, OrderItem
from users.models import User
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "size",
            "quantity",
            "price",
        ]


class AdminOrderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_name",
            "total_amount",
            "payment_method",
            "status",
            "created_at",
            "items",
        ]
