from django.db import models
from django.conf import settings


class Timestamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Announcement(Timestamp):
    title = models.CharField(max_length=100)
    link = models.URLField()
    banner = models.ImageField(upload_to="announcement_banners")

    def __str__(self):
        return self.title


class Company(Timestamp):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return  self.name


class Ship(Timestamp):
    company = models.ForeignKey(Company, related_name='ships', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name






