from django.urls import path

from . import views

urlpatterns = [
    path("", views.ListingList.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<str:username>/edit", views.UserUpdate.as_view(), name="update_user"),
    path("user/<str:username>", views.UserDetail.as_view(), name="user_page"),
    path("category/create", views.CategoryCreate.as_view(), name="create_category"),
    path("category/<str:slug>", views.CategoryDetail.as_view(), name="category"),
    path("category", views.CategoryList.as_view(), name="categories"),
    path("listing/<int:id>/edit", views.ListingUpdate.as_view(), name="update_listing"),
    path("listing/<int:id>/close", views.ListingClose.as_view(), name="close_listing"),
    path("listing/<int:id>", views.ListingDetail.as_view(), name="listing"),
    path("listing/new", views.ListingCreate.as_view(), name="create_listing"),    
    path("watchlist", views.WatchlistDetail.as_view(), name="watchlist")
]
