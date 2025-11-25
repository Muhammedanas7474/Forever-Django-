from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Cart
from .serializers import CartSerializer
from products.models import Product


class CartListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data, status=200)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]     

    def post(self, request):
        product_id = request.data.get("product_id")
        size = request.data.get("size")
        quantity = request.data.get("quantity", 1)

        if not size:
            return Response({"error": "Size required"}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                size=size,
                defaults={"quantity": quantity}
            )

        if not created:
            item.quantity += int(quantity)
            item.save()


        return Response({"message": "Added to cart"}, status=201)


class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, cart_id):
        return self.update(request, cart_id)

    def put(self, request, cart_id):
        return self.update(request, cart_id)

    def update(self, request, cart_id):
        try:
            item = Cart.objects.get(id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        quantity = request.data.get("quantity")

        if quantity is None:
            return Response({"error": "Quantity required"}, status=400)

        try:
            quantity = int(quantity)
        except:
            return Response({"error": "Invalid quantity"}, status=400)

        if quantity == 0:
            item.delete()
            return Response({"message": "Item removed"}, status=200)

        item.quantity = quantity
        item.save()

        return Response({"message": "Quantity updated"}, status=200)

class DeleteCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_id):
        try:
            item = Cart.objects.get(id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        item.delete()
        return Response({"message": "Item removed"}, status=200)
