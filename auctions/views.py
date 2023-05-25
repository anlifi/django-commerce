from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import NewListingForm, NewBidForm, NewCommentForm
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
        
        # Add listing to watchlist and session
        watchlist.listings.add(listing)
        request.session["watchlist_count"] = watchlist.listings.count()

        # Show success message and return listing page
        messages.success(request, "Listing added to your watchlist.")
        return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
    
    # GET method not allowed
    return render(request, "auctions/error.html", {
        "code": 405,
        "message": "GET method not allowed."
    })


@login_required(login_url="login")
def bid(request, id):    
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
        
        # Check if listing is closed
        if listing.closed is True:
            messages.error(request, "Listing is closed, placing a bid is not possible.")
            return HttpResponseRedirect(reverse("listing", kwargs={"id": id})) 
    
        # Create form instance with POST data and check if valid
        form = NewBidForm(request.POST)
        if form.is_valid():
            # Save form data to model, set bidder and listing
            new_bid = form.save(commit=False)
            new_bid.bidder = request.user
            new_bid.listing = listing

            # Check if bid at least starting bid and greater than highest bid (if any)
            # Bid is lower than starting bid  
            if new_bid.bid_amount < listing.starting_bid:
                # Show error message and return listing page
                messages.error(request, "Bid must be at least as large as starting bid.")
                return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
            
            # Bid is at least as large as starting bid, other bids exist, but not higher than current bid
            elif Bid.objects.filter(listing=listing) and new_bid.bid_amount <= listing.current_bid:
                # Show error message and return listing page
                messages.error(request, "Bid must be higher than current bid.")
                return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
            
            # Bid is at least as large as starting bid, no other bids and/or higher than current bid
            else:
                # Save new bid, save amount as listing's current bid
                new_bid.save()
                listing.current_bid = new_bid.bid_amount
                listing.save()
                
                # Show success message and return listing page
                messages.success(request, "Successfully placed bid.")
                return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
        
        else:
            # If invalid show error message and return form with existing data
            messages.error(request, "Invalid form. Please resubmit.")
            return render(request, "auctions/create.html", {
                "form": form
            })

    # GET method not allowed
    return render(request, "auctions/error.html", {
        "code": 405,
        "message": "GET method not allowed."
    })


def categories(request):
    # Return all categories in categories page
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category(request, category_id):
    # Get category
    try:
        category = Category.objects.get(pk=category_id)
    
    except Category.DoesNotExist:
        return render(request, "auctions/error.html", {
            "code": 404,
            "message": "Category does not exist."
        })

    # Get all active listings in category ordered by creation date
    try:
        listings = Listing.objects.filter(category=category_id, closed=False).order_by("-creation_date")
    
    except Listing.DoesNotExist:
        return render(request, "auctions/error.html", {
            "code": 404,
            "message": "Listings do not exist."
        })
    
    # Return category page with all it's listings
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings
    })


@login_required(login_url="login")
def close(request, id):
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
        
        # Check if user is seller of listing
        if listing.seller != request.user:
            # Show error message and return listing page
            messages.error(request, "Only listing's seller can close auction.")
            return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
        
        # Close auction
        listing.closed = True
        listing.save()

        # Show success message and return listing page
        messages.success(request, "Auction closed.")
        return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
    
    # GET method not allowed
    return render(request, "auctions/error.html", {
        "code": 405,
        "message": "GET method not allowed."
    })


@login_required(login_url="login")
def comment(request, id):
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
        
        # Create form instance with POST data and check if valid
        form = NewCommentForm(request.POST)
        if form.is_valid():
            # Save form data to model, set bidder and listing
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.listing = listing
            new_comment.save()

            # Show success message and return listing page
            messages.success(request, "New comment created.")
            return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
        
        else:
            # Show error message and return listing page
            messages.error(request, "Invalid form. Please resubmit.")
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
            messages.success(request, "New listing created.")
            return HttpResponseRedirect(reverse("listing", kwargs={"id": new_listing.pk}))
        
        else:
            # If invalid show error message and return form with existing data
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

    # Set user and defaults for watchlist and bid
    user = request.user
    watching = False
    bid_count = 0
    highest_bidder = None
    current_bid = False
    bid_form = None
    winner = False

    # Check if listing in watchlist
    if user.is_authenticated and Watchlist.objects.filter(user=user, listings=listing):
        watching = True

    # Check if bids exist
    if user.is_authenticated and Bid.objects.filter(listing=listing):
        # Get bid count
        bid_count = Bid.objects.filter(listing=listing).count()

        # Check if highest bid is user's
        highest_bid = Bid.objects.filter(listing=listing).order_by("-bid_amount").first()
        highest_bidder = highest_bid.bidder
        if highest_bidder == request.user:
            current_bid = True

            # Check if auction is closed
            if listing.closed:
                winner = True

    # New bid form
    bid_form = NewBidForm()

    # New comment form
    comment_form = NewCommentForm()

    # Get all comments for listing
    comments = Comment.objects.filter(listing=listing).order_by("-date")

    # Return listing page
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watching": watching,
        "bid_count": bid_count,
        "highest_bidder": highest_bidder,
        "current_bid": current_bid,
        "bid_form": bid_form,
        "winner": winner,
        "comment_form": comment_form,
        "comments": comments
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

            # Show success message and return index page
            messages.success(request, "Login successful.")
            return HttpResponseRedirect(reverse("index"))
        
        else:
            # Show error message and return login page
            messages.error(request, "Invalid username and/or password.")
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    # Logout user, show success message and return index page
    logout(request)
    messages.success(request, "Logout successful.")
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            # Show error message and return registration form
            messages.error(request, "Passwords must match.")
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            # Show error message and return registration form
            messages.error(request, "Username already taken.")
            return render(request, "auctions/register.html")
        
        # Login user, show success message and return index page
        login(request, user)
        messages.success(request, "Registration successful." )
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
            request.session["watchlist_count"] = watchlist.listings.count()

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


@login_required(login_url="login")
def watchlist(request):
    # Check if watchlist exists
    try:
        watchlist = Watchlist.objects.get(user=request.user)
    except Watchlist.DoesNotExist:
        # Return empty watchlist
        return render(request, "auctions/watchlist.html")
    
    # Get listings in watchlist and number of listings
    listings = watchlist.listings.all()
    count = listings.count()

    # Return watchlist page with listings
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "count": count
    })