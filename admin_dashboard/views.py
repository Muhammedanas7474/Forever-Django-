from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from django.db.models import Sum, Count
from admin_user.permissions import IsAdminRole
from django.db.models.functions import TruncDate
from datetime import timedelta

from order.models import Order, OrderItem
from users.models import User
from products.models import Product


class DashboardStatsAPIView(APIView):
    authentication_classes = []  # Use default authentication classes
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        today = now().date()

        total_orders = Order.objects.count()
        total_customers = User.objects.filter(role="user").count()
        total_products = Product.objects.count()
        in_stock = Product.objects.filter(stock_count__gt=0).count()
        out_of_stock = Product.objects.filter(stock_count__lte=0).count()
        low_stock = Product.objects.filter(stock_count__lt=10, stock_count__gt=0).count()



        delivered_orders = Order.objects.filter(status="delivered").count()
        pending_orders = Order.objects.filter(status="pending").count()

        total_revenue = (
            Order.objects.filter(status="delivered").aggregate(total=Sum("total_amount"))["total"] or 0
        )

        
        sales_chart = (
            Order.objects.filter(status="delivered")
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(total=Sum("total_amount"))
            .order_by("date")
        )

       
        top_products = (
            OrderItem.objects.values("product__name")
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")[:5]
        )

        
        order_status = (
            Order.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return Response({
            "total_orders": total_orders,
            "total_customers": total_customers,
            "total_products": total_products,
            "delivered_orders": delivered_orders,
            "pending_orders": pending_orders,
            "total_revenue": total_revenue,
            "sales_chart": list(sales_chart),
            "top_products": list(top_products),
            "order_status": list(order_status),
            "stock_summary": {
                "in_stock": in_stock,
                "out_of_stock": out_of_stock,
                "low_stock": low_stock
            }
        })

