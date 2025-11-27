from django.urls import path
from .views import RegisterAPIView,LoginAPIView,LogoutAPIView,UserAPIView
from cart.views import CartListView,AddToCartView,DeleteCartItemView,UpdateCartQuantityView
from products.views import CategoryListAPIView,ProductCreateAPIView,ProductDetailAPIView,ProductListAPIView,RelatedProductsAPIView
from wishlist.views import WishlistAPIView
from order.views import OrderListCreateView,RazorpayOrderCreateView,RazorpayVerifyView


urlpatterns=[
    path('register/',RegisterAPIView.as_view(),name='register'),
    path('login/',LoginAPIView.as_view(),name='login'),
    path('user/',UserAPIView.as_view(),name="user"),
    path('logout/',LogoutAPIView.as_view(),name='logout'),
    
    path('cart/',CartListView.as_view(),),
    path('cart/add/',AddToCartView.as_view()),
    path('cart/update/<int:cart_id>/',UpdateCartQuantityView.as_view()),
    path('cart/delete/<int:cart_id>/',DeleteCartItemView.as_view()),

    path("categories/", CategoryListAPIView.as_view()),
    path("products/", ProductListAPIView.as_view()),
    path("products/create/", ProductCreateAPIView.as_view()),
    path("products/<int:pk>/", ProductDetailAPIView.as_view()),
    path("products/<int:pk>/related/", RelatedProductsAPIView.as_view(), name="related_products"),

    path("wishlist/",WishlistAPIView.as_view()),

    path("order/", OrderListCreateView.as_view()),   
    path("order/razorpay/create/", RazorpayOrderCreateView.as_view()),
    path("order/razorpay/verify/", RazorpayVerifyView.as_view()),
]