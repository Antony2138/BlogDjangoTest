from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .decorators import require_superuser
from .forms import ImageUploadForm, ReviewForm
from .models import ImageCarousel, Review


def index(request):
    carousel = ImageCarousel.objects.all()
    review_form = ReviewForm()
    return render(request, "mainController/index.html", {"review_form": review_form, "carousel": carousel})


@login_required
def submit_review(request):
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.save()
            response = HttpResponse(status=204)
            response['HX-Trigger'] = "add-review"
            return response
    return


def about(request):
    return render(request, "mainController/about.html")


def style(request):
    return render(request, "mainController/style.html")


def promo(request):
    return render(request, "mainController/promo.html")


def calendar_style(request):
    return render(request, "mainController/calendar.html")


def update_reviews(request):
    reviews = Review.objects.all().order_by("-created_at")[:20]
    star_range = range(1, 6)
    return render(request, "mainController/partials/rew_container.html", {"reviews": reviews, "star_range": star_range})


@login_required
@require_superuser
def upload_images(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('image')

            if len(images) < 4:
                messages.error(request, "Для корректной работы карусели необходимо загрузить минимум 4 изображения.")
                return redirect('upload_images')

            ImageCarousel.objects.all().delete()
            for image in images:
                ImageCarousel.objects.create(image=image)
            messages.success(request, "Фотографии загружены успешно!")
            return redirect('upload_images')
        else:
            return HttpResponse("Ошибка загрузки файлов.")
    else:
        form = ImageUploadForm()
    return render(request, 'mainController/upload_images.html', {'form': form})
