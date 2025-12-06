from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from products.models import Product, ProductImage
from admin_user.permissions import IsAdminRole
from .serializer import AdminProductSerializer, AdminProductCreateSerializer


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class AdminProductListView(APIView):
    
    permission_classes = [IsAuthenticated, IsAdminRole]
    pagination_class = ProductPagination

    def get(self, request):
        products = Product.objects.all().order_by('-id')
        search = request.query_params.get("search")

        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(id__icontains=search)
            )

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(products, request)
        serializer = AdminProductSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AdminProductCreateSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()

            
            images = request.FILES.getlist("images")
            for img in images:
                ProductImage.objects.create(product=product, image=img)

            output = AdminProductSerializer(product)
            return Response(
                {"message": "Product created successfully", "product": output.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProductDetailView(APIView):
    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminProductSerializer(product, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_200_OK)
