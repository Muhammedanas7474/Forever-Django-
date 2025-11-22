from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Product(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_count = models.PositiveIntegerField(default=0)
    category=models.ForeignKey(Category,related_name="products",on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    sizes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product=models.ForeignKey(Product,related_name="images",on_delete=models.CASCADE)
    image=CloudinaryField("image")

    def __str__(self):
        return f"Image for {self.product.name}"
