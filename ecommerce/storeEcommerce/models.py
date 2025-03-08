
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Customer(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=False)
    phone = models.CharField(max_length=20, blank=True, null=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customer_set",  # Evita conflictos con el modelo original
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customer_permissions_set",  # Evita conflictos con el modelo original
        blank=True
    )

    # EL campo USERNAME_FIELD es el campo que se usará para autenticar al usuario
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'Customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

# Model for the products in the database
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

# Model for for the orders in the database
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderItem")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"
    

# Model for the items in the orders in the database
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
    
    class Meta:
        db_table = 'Items'
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

