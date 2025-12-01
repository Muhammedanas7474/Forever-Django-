from rest_framework import serializers
from products.models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class AdminProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock_count",
            "category",
            "category_name",
            "active",
            "sizes",
            "created_at",
            "updated_at",
            "images",
        ]


class AdminProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "stock_count",
            "category",
            "active",
            "sizes",
            "images",
        ]

    def validate(self, attrs):
        
        if not attrs.get("name"):
            raise serializers.ValidationError({"name": "Product name is required"})

     
        if not attrs.get("description"):
            raise serializers.ValidationError({"description": "Product description is required"})

       
        price = attrs.get("price")
        if price is None or price <= 0:
            raise serializers.ValidationError({"price": "Price must be a positive number"})

       
        stock = attrs.get("stock_count")
        if stock is None or stock < 0:
            raise serializers.ValidationError({"stock_count": "Stock count must be 0 or greater"})

       
        if not attrs.get("category"):
            raise serializers.ValidationError({"category": "Category is required"})

       
        sizes = attrs.get("sizes")
        if not sizes or len(sizes) == 0:
            raise serializers.ValidationError({"sizes": "At least one size is required"})

        
        images = attrs.get("images")
        if not images or len(images) == 0:
            raise serializers.ValidationError({"images": "At least one product image is required"})

        return attrs

    def create(self, validated_data):
        images = validated_data.pop("images")
        product = Product.objects.create(**validated_data)

        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return product