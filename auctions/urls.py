from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("closed", views.closed, name="closed"),
    path("create", views.create, name="create"),
    path("listings/<int:id>", views.listing, name="listing"),
    path("listings/<int:id>/add", views.addWatchlist, name="add"),
    path("listings/<int:id>/bid", views.bid, name="bid"),
    path("listings/<int:id>/close", views.close, name="close"),
    path("listings/<int:id>/comment", views.comment, name="comment"),
    path("listings/<int:id>/edit", views.edit, name="edit"),
    path("listings/<int:id>/remove", views.removeWatchlist, name="remove"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
]
