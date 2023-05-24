from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("listings/<str:id>", views.listing, name="listing"),
    path("listings/<str:id>/add", views.addWatchlist, name="add"),
    path("listings/<str:id>/bid", views.bid, name="bid"),
    path("listings/<str:id>/remove", views.removeWatchlist, name="remove"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
]
