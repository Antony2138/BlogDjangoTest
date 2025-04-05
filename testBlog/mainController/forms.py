from django import forms

from .models import ImageCarousel, Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=True
    )
    text = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )

    class Meta:
        model = Review
        fields = ["text", "rating"]


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageCarousel
        fields = ["image"]

        labels = {
            "image": "Фотографии",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget.attrs.update({"multiple": "true"})
