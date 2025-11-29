from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import Http404

from .models import Wishlist
from .serializers import WishlistSerializer
from products.models import Product


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """List all wishlist items"""
        items = (
            Wishlist.objects.filter(user=request.user)
            .select_related("product")
            .order_by("-added_at")
        )
        serializer = WishlistSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Helper to fetch the product
    def get_product(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise Http404("Product not found")

    def post(self, request, format=None):
        """Add product to wishlist"""
        product_id = request.data.get("product_id")

        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        product = self.get_product(product_id)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if created:
            return Response({"message": "Added to wishlist"}, status=status.HTTP_201_CREATED)

        return Response({"message": "Already in wishlist"}, status=status.HTTP_200_OK)

    def delete(self, request, format=None):
        """Clear entire wishlist"""
        Wishlist.objects.filter(user=request.user).delete()
        return Response({"message": "Wishlist cleared"}, status=status.HTTP_200_OK)
class WishlistItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id, format=None):
        """Remove a specific product from wishlist"""
        deleted, _ = Wishlist.objects.filter(
            user=request.user,
            product_id=product_id
        ).delete()

        if deleted:
            return Response({"message": "Item removed"}, status=status.HTTP_200_OK)

        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
