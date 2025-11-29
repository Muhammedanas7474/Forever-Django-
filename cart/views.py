from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import Http404

from .models import Cart
from .serializers import CartSerializer
from products.models import Product


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    # List all cart items
    def get(self, request, format=None):
        items = (
            Cart.objects.filter(user=request.user)
            .select_related("product")
            .order_by("-created_at")
        )
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Add product / update quantity
    def post(self, request, format=None):
        product_id = request.data.get("product_id")
        size = request.data.get("size", "")  # ✅ Get size from request
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate size is provided
        if not size:
            return Response({"error": "size is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # STOCK CHECK
        if product.stock_count == 0:
            return Response({"error": "Sorry, this product is out of stock"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Include size in get_or_create
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            size=size  # ✅ This is the key fix!
        )

        if not created:
            if cart_item.quantity + quantity > product.stock_count:
                return Response(
                    {"error": f"Only {product.stock_count} left in stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity += quantity
        else:
            if quantity > product.stock_count:
                return Response(
                    {"error": f"Only {product.stock_count} left in stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = quantity

        cart_item.save()
        return Response(CartSerializer(cart_item).data, status=status.HTTP_200_OK)

    # Clear entire cart
    def delete(self, request, format=None):
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)
    
class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    # PUT → Update quantity (for your current frontend)
    def put(self, request, item_id, format=None):
        try:
            cart_item = Cart.objects.get(id=item_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            quantity = int(request.data.get("quantity", 1))
        except ValueError:
            return Response({"error": "quantity must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        stock = cart_item.product.stock_count

        # Out of stock check
        if stock == 0:
            return Response({"error": "This product is out of stock"}, status=status.HTTP_400_BAD_REQUEST)

        # Stock validation
        if quantity > stock:
            return Response({"error": f"Only {stock} left in stock"}, status=status.HTTP_400_BAD_REQUEST)

        # Do not go below 1
        if quantity < 1:
            quantity = 1

        cart_item.quantity = quantity
        cart_item.save()

        return Response(CartSerializer(cart_item).data, status=status.HTTP_200_OK)

    # PATCH → Increment / decrement quantity (optional)
    def patch(self, request, item_id, format=None):
        try:
            cart_item = Cart.objects.get(id=item_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            delta = int(request.data.get("delta", 0))
        except ValueError:
            return Response({"error": "delta must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        new_quantity = cart_item.quantity + delta
        stock = cart_item.product.stock_count

        # Out of stock check
        if stock == 0:
            return Response({"error": "This product is out of stock"}, status=status.HTTP_400_BAD_REQUEST)

        # Stock validation
        if new_quantity > stock:
            return Response({"error": f"Only {stock} left in stock"}, status=status.HTTP_400_BAD_REQUEST)

        # Do not go below 1
        if new_quantity < 1:
            new_quantity = 1

        cart_item.quantity = new_quantity
        cart_item.save()

        return Response(CartSerializer(cart_item).data, status=status.HTTP_200_OK)

    # DELETE → Remove item
    def delete(self, request, item_id, format=None):
        deleted = Cart.objects.filter(id=item_id, user=request.user).delete()

        if deleted[0] > 0:
            return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)