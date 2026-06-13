from django.db import models
from django.utils import timezone
from user.models import User
# Create your models here.
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return timezone.now() > self.valid_until

    @classmethod
    def delete_expired(cls):
        cls.objects.filter(valid_until__isnull=False, valid_until__lte=timezone.now()).delete()

    def __str__(self):
        return self.name