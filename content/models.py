from django.db import models


class Text(models.Model):
    text = models.TextField()

    def __str__(self):
        return str(self.text)


class Photo(models.Model):
    photo = models.ImageField(upload_to='contents')

    def __str__(self):
        return self.photo.url


class File(models.Model):
    file = models.FileField(upload_to='contents')

    def __str__(self):
        return self.file.url

