from django.urls import path
from .views import RegisterAPIView,LoginAPIView,LogoutAPIView,UserAPIView
from cart.views import CartView,CartItemView
from products.views import CategoryListAPIView,ProductCreateAPIView,ProductDetailAPIView,ProductListAPIView,RelatedProductsAPIView
from wishlist.views import WishlistView,WishlistItemView
from order.views import OrderListCreateView,RazorpayOrderCreateView,RazorpayVerifyView



urlpatterns=[
    path('register/',RegisterAPIView.as_view(),name='register'),
    path('login/',LoginAPIView.as_view(),name='login'),
    path('user/',UserAPIView.as_view(),name="user"),
    path('logout/',LogoutAPIView.as_view(),name='logout'),
    
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/item/<int:item_id>/", CartItemView.as_view(), name="cart_item"),

    path("categories/", CategoryListAPIView.as_view(), name="category_list"),
    path("products/", ProductListAPIView.as_view(), name="product_list"),
    path("products/create/", ProductCreateAPIView.as_view(), name="product_create"),
    path("products/<int:pk>/", ProductDetailAPIView.as_view(), name="product_detail"),
    path("products/<int:pk>/related/", RelatedProductsAPIView.as_view(), name="related_products"),

    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path("wishlist/item/<int:product_id>/", WishlistItemView.as_view(), name="wishlist_item"),

    path("order/", OrderListCreateView.as_view()),   
    path("order/razorpay/create/", RazorpayOrderCreateView.as_view()),
    path("order/razorpay/verify/", RazorpayVerifyView.as_view()),

    
]