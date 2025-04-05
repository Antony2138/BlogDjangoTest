from django.contrib import admin

from .models import ImageCarousel, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(ImageCarousel)
class ImageCarouselAdmin(admin.ModelAdmin):
    pass
