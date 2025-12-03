from django.http import Http404
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from .models import Product, Category
from .serializers import ProductCreateSerializer, ProductSerializer,CategorySerializer



class CategoryListAPIView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ProductCreateAPIView(APIView):
    
    def post(self, request, format=None):
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductListAPIView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request, format=None):
        products = Product.objects.all()

        
        category = request.GET.get("category")
        if category:
            products = products.filter(category_id=category)

        min_price = request.GET.get("min_price")
        if min_price:
            products = products.filter(price__gte=min_price)

        max_price = request.GET.get("max_price")
        if max_price:
            products = products.filter(price__lte=max_price)

        
        search = request.GET.get("search")
        if search:
            products = products.filter(name__icontains=search)

        
        sort = request.GET.get("sort")
        if sort == "price_asc":
            products = products.order_by("price")
        elif sort == "price_desc":
            products = products.order_by("-price")
        elif sort == "newest":
            products = products.order_by("-created_at")

       
        page = request.GET.get("page", 1)
        paginator = Paginator(products, 10)
        paginated_products = paginator.get_page(page)

        serializer = ProductSerializer(paginated_products, many=True)

        return Response({
            "total_products": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": paginated_products.number,
            "products": serializer.data
        }, status=status.HTTP_200_OK)



class ProductDetailAPIView(APIView):
    permission_classes = [AllowAny] 
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)



class RelatedProductsAPIView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request, pk, format=None):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        related_products = Product.objects.filter(
            category_id=product.category_id
        ).exclude(id=pk).order_by("-created_at")[:8]

        serializer = ProductSerializer(related_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
