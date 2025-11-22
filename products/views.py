from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import  get_object_or_404
from .models import Product,Category,ProductImage
from .serializers import ProductCreateSerializer,ProductImageSerializer,ProductSerializer
from django.core.paginator import Paginator

# Create your views here.

class CategoryListAPIView(APIView):
    def get(self,request):
        categories=Category.objects.all()
        data=[{"id":c.id,"name":c.name} for c in categories]
        return Response(data)
    
class ProductCreateAPIView(APIView):
    def post(self,request):
        serializer=ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            product=serializer.save()
            return Response({"messege":"Product created successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)
    
class ProductListAPIView(APIView):
    def get(self,request):
        products=Product.objects.all()

        category=request.GET.get('category')
        if category:
            products=products.filter(category_id=category)

        min_price=request.GET.get('min_price')
        if min_price:
            products=products.filter(price__gte=min_price)

        max_price=request.GET.get('max_price')
        if max_price:
            products=products.filter(price__lte=max_price)
        
        search=request.GET.get('search')
        if search:
            products=products.filter(name__icontains=search)
        

        sort=request.GET.get('sort')
        if sort == "price_asc":
            products=products.order_by('price')
        elif sort == 'price_desc':
            products =products.order_by('-price')
        elif sort == 'newest':
            products=products.order_by('-created_at')
        

        page=request.GET.get("page",1)
        paginator=Paginator(products,10)
        paginated_products=paginator.get_page(page)



        serializer=ProductSerializer(paginated_products,many=True)
        return Response({
            "total_products": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": paginated_products.number,
            "products": serializer.data
        }, status=status.HTTP_200_OK)


class ProductDetailAPIView(APIView):
    def get(self,request,pk):
        product=get_object_or_404(Product,id=pk)
        serializer=ProductSerializer(product)
        return Response(serializer.data)
    


