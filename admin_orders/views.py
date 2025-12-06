from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from admin_user.permissions import IsAdminRole
from rest_framework_simplejwt.authentication import JWTAuthentication


from order.models import Order
from .serializer import AdminOrderSerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class AdminOrderListView(APIView):
    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminRole]
    pagination_class = OrderPagination

    def get(self, request):
        
        orders = Order.objects.all().order_by("-created_at")

      
        search = request.query_params.get("search")
        if search:
            orders = orders.filter(
                Q(id__icontains=search) |
                Q(user__username__icontains=search) |
                Q(status__icontains=search)
            )

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(orders, request)
        serializer = AdminOrderSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class AdminOrderDetailView(APIView):
    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request, pk):
        try:
            order = Order.objects.prefetch_related("items").get(id=pk)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=404)

        serializer = AdminOrderSerializer(order)
        return Response(serializer.data, status=200)

    def patch(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=404)

        new_status = request.data.get("status")
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Invalid status value"}, status=400)

        order.status = new_status
        order.save()

        return Response({"message": "Order status updated", "status": order.status}, status=200)
