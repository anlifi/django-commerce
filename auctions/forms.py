from django.forms import ModelForm

from .models import Listing


class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image_url", "category"]