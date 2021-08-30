from django.contrib import admin

from .models import User, ListingCategory, Listing, Bid, Comment

admin.site.register([User, ListingCategory, Listing, Bid, Comment])