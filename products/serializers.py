from rest_framework import serializers
from .models import Category,Product,ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["url"]

    def get_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url



class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock_count',
            'category', 'category_name', 'sizes', 'active',
            'images', 'created_at', 'updated_at'
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Product
        fields = [
            "name", "description", "price", "category",
            "sizes", "images", "stock_count"
        ]

    def create(self, validated_data):
        images = validated_data.pop("images")
        product = Product.objects.create(**validated_data)

        ProductImage.objects.bulk_create([
            ProductImage(product=product, image=img) for img in images
        ])

        return product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
