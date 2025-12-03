from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from django.db.models import Sum
from admin_user.permissions import IsAdminRole

from order.models import Order
from users.models import User
from products.models import Product


class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        today = now().date()

        total_orders = Order.objects.count()
        total_customers = User.objects.filter(role="user").count()
        total_products = Product.objects.count()

        delivered_orders = Order.objects.filter(status="delivered").count()
        pending_orders = Order.objects.filter(status="pending").count()

        total_revenue = Order.objects.filter(status="delivered").aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        today_sales = Order.objects.filter(
            status="delivered",
            created_at__date=today
        ).aggregate(total=Sum("total_amount"))["total"] or 0

        recent_orders_qs = Order.objects.order_by("-created_at")[:5]

        recent_orders = [
            {
                "id": order.id,
                "user": order.user.username,
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at,
            }
            for order in recent_orders_qs
        ]

        return Response({
            "total_orders": total_orders,
            "total_customers": total_customers,
            "total_products": total_products,
            "delivered_orders": delivered_orders,
            "pending_orders": pending_orders,
            "total_revenue": total_revenue,
            "today_sales": today_sales,
            "recent_orders": recent_orders,
        })
