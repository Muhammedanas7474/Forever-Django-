from django.urls import path
from .views import (
    CategoryListAPIView,
    ProductCreateAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
)

urlpatterns = [
    path("categories/", CategoryListAPIView.as_view()),
    path("products/", ProductListAPIView.as_view()),
    path("products/create/", ProductCreateAPIView.as_view()),
    path("products/<int:pk>/", ProductDetailAPIView.as_view()),
]
