from django.contrib.auth import get_user_model
from django.db import models


class Review(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} ({self.rating}★)"


class ImageCarousel(models.Model):
    description = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to="carousel/", blank=True, null=True)

    def get_image_url(self):
        if not self.image:
            return ""
        return self.image.url
