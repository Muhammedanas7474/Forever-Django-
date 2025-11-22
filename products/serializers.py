from rest_framework import serializers
from .models import Category,Product,ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    url=serializers.SerializerMethodField()

    class Meta:
        model=ProductImage
        fields=["url"]

    def get_url(self,obj):
        return obj.image.url
    


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock_count',
            'category', 'sizes', 'active', 'images',
            'created_at', 'updated_at'
        ]

class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "category",
            "sizes",
            "images",
        ]

    def create(self, validated_data):
        images = validated_data.pop("images")
        product = Product.objects.create(**validated_data)

        for img in images:
            ProductImage.objects.create(product=product, image=img)

        return product

