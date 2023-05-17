from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import NewListingForm
from .models import User, Category, Listing, Bid, Comment, Watchlist


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
    return render(request, "auctions/index.html")


def listing(request, id):
    # Get listing by id and show listing page
    listing = Listing.objects.get(pk=id)
    return render(request, "auctions/listing.html", {
        "listing": listing
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
