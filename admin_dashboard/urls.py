from django.urls import path
from admin_user.views import AdminDetailView,AdminUserListView
from admin_product.views import AdminProductListView,AdminProductDetailView
from admin_orders.views import AdminOrderDetailView,AdminOrderListView
from .views import DashboardStatsAPIView


urlpatterns = [
    path("users/", AdminUserListView.as_view(), name="admin-users-list"),
    path("users/<int:pk>/", AdminDetailView.as_view(), name="admin-user-detail"),

    path('products/',AdminProductListView.as_view()),
    path('products/<int:pk>/',AdminProductDetailView.as_view()),

    path("orders/", AdminOrderListView.as_view()),
    path("orders/<int:pk>/", AdminOrderDetailView.as_view()),

    path("dashboard/", DashboardStatsAPIView.as_view(), name="admin-dashboard"),
    
]