from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import NewListingForm
from .models import User, Category, Listing, Bid, Comment, Watchlist


@login_required(login_url="login")
def addWatchlist(request, id):
    # Only POST method allowed
    if request.method == "POST":
        # Check if listing exists
        try:
            listing = Listing.objects.get(pk=id)
        
        except Listing.DoesNotExist:
            return render(request, "auctions/error.html", {
                "code": 404,
                "message": "The listing does not exist."
            })

        # Check if user's watchlist exists else create new one
        try:
            watchlist = Watchlist.objects.get(user=request.user)
        
        except Watchlist.DoesNotExist:
            watchlist = Watchlist.objects.create(user=request.user)
        
        # Check if listing already in watchlist
        if Watchlist.objects.filter(user=request.user, listings=listing):
            # Show error message and return to listing page
            messages.error(request, "This listing is already in your watchlist.")
            return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
        
        # Add listing to watchlist
        watchlist.listings.add(listing)

        # Show success message and return listing page
        messages.success(request, "Listing added to your watchlist.")
        return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
    
    # GET method not allowed
    return render(request, "auctions/error.html", {
        "code": 405,
        "message": "GET method not allowed."
    })


def create(request):
    if request.method == "POST":

        # Create form instance with POST data and check if valid
        form = NewListingForm(request.POST)
        if form.is_valid():
            
            # Save form data to model, set seller and current_bid
            new_listing = form.save(commit=False)
            new_listing.seller = request.user
            new_listing.current_bid = new_listing.starting_bid
            new_listing.save()

            # Show success message and return page with new listing
            messages.success(request, "New Listing created.")
            return HttpResponseRedirect(reverse("listing", kwargs={"id": new_listing.pk}))
        
        else:
            # If invalid show error message and return form with existing data
            form = NewListingForm(request.POST)
            messages.error(request, "Invalid form. Please resubmit.")
            return render(request, "auctions/create.html", {
                "form": form
            })
    
    # Show form for new listing
    form = NewListingForm()
    return render(request, "auctions/create.html", {
        "form": form
    })


def index(request):
    # Get all active listings
    listings = Listing.objects.filter(closed=False)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def listing(request, id):
    # Check if listing exists
    try:
        listing = Listing.objects.get(pk=id)
    
    except Listing.DoesNotExist:
        return render(request, "auctions/error.html", {
            "code": 404,
            "message": "The listing does not exist."
        })

    # Set user and defaults for watchlist
    user = request.user
    watching = False

    # Check if listing in watchlist
    if user.is_authenticated and Watchlist.objects.filter(user=user, listings=listing):
        watching = True

    # Return listing page
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watching": watching
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="login")
def removeWatchlist(request, id):
    # Only POST method allowed
    if request.method == "POST":
        # Check if listing exists
        try:
            listing = Listing.objects.get(pk=id)
        
        except Listing.DoesNotExist:
            return render(request, "auctions/error.html", {
                "code": 404,
                "message": "The listing does not exist."
            })
        
        # Check if listing in watchlist
        if Watchlist.objects.filter(user=request.user, listings=listing):
            # Get user's watchlist
            watchlist = Watchlist.objects.get(user=request.user)

            # Remove listing from watchlist
            watchlist.listings.remove(listing)

            # Show success message an return listing page
            messages.success(request, "Listing removed your watchlist.")
            return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
        
        else:
            # Show error message and return listing page
            messages.error(request, "Cannot remove listing not in your watchlist.")
            return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
    
    # GET method not allowed
    return render(request, "auctions/error.html", {
        "code": 405,
        "message": "GET method not allowed."
    })