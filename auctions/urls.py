from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<str:username>", views.user, name="user_page"),
    path("category/<str:slug>", views.category, name="category"),
    path("category", views.categories, name="categories"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("create-listing", views.create_listing, name="create_listing"),
    path("watchlist", views.watchlist, name="watchlist")
]
