from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("submit_review/", views.submit_review, name="submit_review"),
    path("update_reviews/", views.update_reviews, name="update_reviews"),
    path("about", views.about, name="about"),
    path("style", views.style, name="style"),
    path("promo", views.promo, name="promo"),
    path("calendar", views.calendar_style, name="calendar"),
    path('upload_images/', views.upload_images, name='upload_images'),

]
