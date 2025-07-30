from django.db import models


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

