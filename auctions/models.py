from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class User(AbstractUser):
    avatar = models.URLField(
        max_length=400,
        blank=True
    )

    def get_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_absolute_url(self):        
        return reverse("user_page", kwargs={
            "username": self.username
        })
    
    def get_update_url(self):
        return reverse("update_user", kwargs={
            "username": self.username
        })


class ListingCategory(models.Model):
    name = models.CharField(max_length=63)
    slug = models.SlugField(
        max_length=63,
        unique=True
    )

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("category", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ListingCategory, self).save(*args, **kwargs)
    

class Listing(models.Model):
    author = models.ForeignKey(
        User,        
        on_delete=models.CASCADE,
        related_name="created_listings"
    )
    title = models.CharField(max_length=63)
    description = models.TextField()
    category = models.ForeignKey(
        ListingCategory,        
        on_delete=models.CASCADE,                
        null=True,
        blank=True,
        related_name="listings",
    )
    date_added = models.DateTimeField(auto_now_add=True)
    starting_bid = models.FloatField()
    image = models.URLField(
        max_length=400,
        blank=True
    )
    watchlisted_by = models.ManyToManyField(
        User,       
        blank=True,        
        related_name="watchlist_listings"
    )
    user_with_max_bid = models.ForeignKey(
        User,        
        on_delete=models.CASCADE,        
        null=True      
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    def get_absolute_url(self):
        return reverse("listing", kwargs={"id": self.pk})

    def get_update_url(self):
        return reverse("update_listing", kwargs={"id": self.pk})
    
    def get_close_url(self):
        return reverse("close_listing", kwargs={"id": self.pk})
    
    def calculate_current_price(self):
        return self.bids.aggregate(models.Max('amount'))["amount__max"] or self.starting_bid
    
    def calculate_max_bid(self):
        return self.bids.aggregate(models.Max('amount'))["amount__max"] or 0

    class Meta:    
        ordering = ['-date_added', 'title']
        get_latest_by = 'date_added'


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
    date_added = models.DateTimeField(blank=True ,auto_now_add=True)

    def __str__(self):
        return f"On {self.on_listing.title} from {self.from_user} [amount={self.amount}]"
    
    class Meta:    
        ordering = ['-date_added']
        get_latest_by = 'date_added'


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
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.author} on {self.on_listing.title}"
    
    class Meta:    
        ordering = ['-date_added']
        get_latest_by = 'date_added'