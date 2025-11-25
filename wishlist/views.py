from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist
from .serializers import WishlistSerializer
from rest_framework.response import Response
from rest_framework import status
from products.models import Product

# Create your views here.


class WishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Wishlist.objects.filter(user=request.user).select_related("product")
        serializer = WishlistSerializer(items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"error": "product_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        return Response({"message": "Product added to wishlist"}, status=200)
    
    def delete(self, request):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"error": "product_id required"}, status=400)
        
        deleted, _ = Wishlist.objects.filter(user=request.user, product_id=product_id).delete()

        if deleted:
            return Response({"message": "Removed"}, status=200)
        return Response({"error": "Not found"}, status=404)
