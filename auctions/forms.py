from django.forms import ModelForm

from .models import Listing, Bid


class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image_url", "category"]


class NewBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["bid_amount"]
        labels = {
            "bid_amount": ""
        }
    
    def __init__(self, *args, **kwargs):
        super(NewBidForm, self).__init__(*args, **kwargs)

        self.fields["bid_amount"].widget.attrs["placeholder"] = "Bid"