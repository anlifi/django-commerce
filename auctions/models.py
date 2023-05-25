from django.contrib.auth.models import AbstractUser
from django.db import models


NONE = "NONE"
FASH = "FASH"
HOME = "HOME"
TOYS = "TOYS"
ELEC = "ELEC"
PETS = "PETS"
GARD = "GARD"

CATEGORY_CHOICES = [
    (NONE, "Other"),
    (FASH, "Fashion"),
    (TOYS, "Toys"),
    (ELEC, "Electronics"),
    (PETS, "Pets"),
    (GARD, "Garden"),
]


class User(AbstractUser):
    pass

    def __str__(self):
        return f"User ID: {self.pk}, Username: {self.username}"
    
    def get_username(self):
        return self.username
    
    def get_watchlist_items(self):
        return self.user_watchlist.first().listings.count()


class CategoryManager(models.Manager):
    def create_category(self, name):
        return self.create(name=name)
    
    def get_default_category(self):
        return self.get(name=dict(CATEGORY_CHOICES)[NONE])


class Category(models.Model):
    name = models.CharField(max_length=64)

    objects = CategoryManager()

    def __str__(self):
        return self.name
    

# Initialize all categories
for _, name in CATEGORY_CHOICES:
    if not Category.objects.filter(name=name).exists():
        Category.objects.create_category(name)


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=255)
    starting_bid = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    current_bid = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    image_url = models.URLField(max_length=255, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_listings", blank=True, default=Category.objects.get_default_category)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_listings")
    closed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Listing ID: {self.pk}, Title: {self.title}, Seller: {self.seller}, Closed: {self.closed}"
 
    
class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    bid_amount = models.DecimalField(max_digits=9, decimal_places=2)
    bid_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bidder: {self.bidder}, Listing: {self.listing}, Amount: {self.bid_amount}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    title = models.CharField(max_length=64)
    content = models.TextField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")

    def __str__(self):
        return f"User: {self.user}, Comment on: {self.listing}"
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_watchlist")
    listings = models.ManyToManyField(Listing, related_name="listings_in_watchlist", blank=True)

    def __str__(self):
        return f"Watchlist User: {self.user}"
