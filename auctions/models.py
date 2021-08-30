from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    pass

    def get_absolute_url(self):
        return reverse("user_page", kwargs={"login": self.username})


class ListingCategory(models.Model):
    name = models.CharField(max_length=63)
    slug = models.SlugField(
        max_length=31,
        unique=True
    )

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("category", kwargs={"slug": self.slug})
    

class Listing(models.Model):
    name = models.CharField(max_length=63)
    author = models.ForeignKey(
        User,        
        on_delete=models.CASCADE,
        related_name="created_listings"
    )
    category = models.ForeignKey(
        ListingCategory,        
        on_delete=models.CASCADE,
        related_name="listings"
    )
    starting_bid = models.FloatField()
    image = models.URLField(blank=True)
    watchlisted_by = models.ManyToManyField(
        User,
        blank=True,        
        related_name="watchlist_listings"
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} by {self.author}"

    def get_absolute_url(self):
        return reverse("listing", kwargs={"id": self.pk})


class Bid(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bids"
    )
    on_listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bids"
    )
    amount = models.FloatField()

    def __str__(self):
        return f"On {self.on_listing.name} from {self.from_user} [amount={self.amount}]"


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    on_listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    text = models.TextField()

    def __str__(self):
        return f"From {self.author} on {self.on_listing.name}"