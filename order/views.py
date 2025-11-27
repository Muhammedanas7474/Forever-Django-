from decimal import Decimal
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart  
from django.conf import settings
import razorpay


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        """
        This handles COD orders.
        Razorpay online payment will use a separate verify endpoint.
        """
        payment_method = request.data.get("payment_method", "cod")
        if payment_method != "cod":
            return Response(
                {"error": "Use Razorpay endpoint for online payment"},
                status=400,
            )

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        # Calculate total from backend (never trust frontend amount)
        total_amount = Decimal("0.00")
        for item in cart_items.select_related("product"):
            total_amount += Decimal(item.product.price) * item.quantity

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                payment_method="cod",
                status="pending",
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.size,
                    quantity=item.quantity,
                    price=item.product.price,
                )

            cart_items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)


class RazorpayOrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        1) Read cart
        2) Calculate total
        3) Create Razorpay order
        4) Return order_id + key to frontend
        """
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total_amount = 0
        for item in cart_items.select_related("product"):
            total_amount += float(item.product.price) * item.quantity

        amount_paise = int(total_amount * 100)  

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1,
            }
        )

        

        return Response(
            {
                "razorpay_order_id": razorpay_order["id"],
                "amount": amount_paise,
                "currency": "INR",
                "key": settings.RAZORPAY_KEY_ID,
            },
            status=200,
        )


from razorpay.errors import SignatureVerificationError


class RazorpayVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Frontend sends: order_id, payment_id, signature
        We verify and then create Order + OrderItems + clear cart
        """
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
            return Response({"error": "Missing payment details"}, status=400)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

       
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            client.utility.verify_payment_signature(params_dict)
        except SignatureVerificationError:
            return Response({"error": "Payment verification failed"}, status=400)

        
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total_amount = Decimal("0.00")
        for item in cart_items.select_related("product"):
            total_amount += Decimal(item.product.price) * item.quantity

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                payment_method="razorpay",
                status="paid",
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature,
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.size,
                    quantity=item.quantity,
                    price=item.product.price,
                )

            cart_items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)
