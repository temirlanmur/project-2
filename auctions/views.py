from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django.core.exceptions import PermissionDenied

from .models import User, ListingCategory, Listing
from .forms import UserForm, ListingForm, CommentForm, BidForm
from .utils import CustomPageRangeMixin


class ListingList(CustomPageRangeMixin, ListView):
    context_object_name = "listings"
    paginate_by = 6
    template_name = "auctions/index.html"

    def get_queryset(self):
        active_listings = Listing.objects.filter(active=True)
        return active_listings
    

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


# Custom views
class UserDetail(View):
    model = User
    template_name = "auctions/user.html"

    def get(self, request, username):
        user = get_object_or_404(self.model, username=username)
        isauthor_flag = (request.user == user)
        return render(request, self.template_name, {
            "user_detail": user,
            "isauthor_flag": isauthor_flag
        })
    

class UserUpdate(View):
    model = User
    form_class = UserForm
    template_name = "auctions/user_update.html"

    def get(self, request, username):
        user = get_object_or_404(self.model, username=username)
        if request.user == user:
            return render(request, self.template_name, {
                "user_detail": user,
                "form": self.form_class(instance=user)
            })
        raise PermissionDenied
        

    def post(self, request, username):
        user = get_object_or_404(self.model, username=username)
        if request.user == user:
            update_form = self.form_class(request.POST, instance=user)
            if update_form.is_valid():
                updated_user = update_form.save()
                return redirect(updated_user)
            else:
                return render(request, self.template_name, {
                    "user_detail": user,
                    "form": update_form
                })
        raise PermissionDenied


class CategoryList(ListView):
    context_object_name = 'categories'
    model = ListingCategory
    template_name = "auctions/category_list.html"


class CategoryDetail(CustomPageRangeMixin, ListView):
    context_object_name = 'listings'
    paginate_by = 6
    template_name = "auctions/category_detail.html"
    
    def get_queryset(self):
        category = get_object_or_404(ListingCategory, slug=self.kwargs['slug'])
        listings = category.listings.filter(active=True)
        return listings


def listing_view(request, id):
    listing = get_object_or_404(Listing, pk=id)     
    isauthor_flag = (request.user == listing.author)
    inwatchlist_flag = listing.watchlisted_by.filter(username=request.user).exists()
    bidlow_flag = False
    bid_form = BidForm()
    comment_form = CommentForm()
    
    if request.method == "POST":
        post_data = request.POST
        # Process watchlist
        if "addtowatchlist" in post_data:            
            if inwatchlist_flag:
                listing.watchlisted_by.remove(request.user)
                inwatchlist_flag = False                   
            else:
                listing.watchlisted_by.add(request.user)
                inwatchlist_flag = True
        # Process bid
        if "makebid" in post_data:
            bid_form = BidForm(post_data)                
            if bid_form.is_valid():
                user_bid = bid_form.cleaned_data["amount"]
                if (user_bid > listing.calculate_max_bid()) and (user_bid >= listing.starting_bid):
                    new_bid = bid_form.save(commit=False)
                    new_bid.from_user = request.user
                    new_bid.on_listing = listing
                    new_bid.save()
                    bid_form = BidForm()
                    listing.user_with_max_bid = request.user
                    listing.save()
                else:
                    bidlow_flag = True                    
        # Process comment
        if "addcomment" in post_data:            
            comment_form = CommentForm(post_data)   
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.author = request.user
                new_comment.on_listing = listing
                new_comment.save()
                comment_form = CommentForm()

    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "isauthor_flag": isauthor_flag,
        "inwatchlist_flag": inwatchlist_flag,
        "bidlow_flag": bidlow_flag,
        "bid_form": bid_form,
        "comment_form": comment_form
    })


class ListingUpdate(LoginRequiredMixin, UpdateView):
    form_class = ListingForm
    login_url = "login"  
    template_name = "auctions/listing_update.html"

    def get_object(self, queryset=None):
        obj = get_object_or_404(Listing, pk=self.kwargs["id"])
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj


class ListingCreate(LoginRequiredMixin, CreateView):  
    form_class = ListingForm
    login_url = "login"
    model = Listing
    template_name = "auctions/listing_create.html"
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        return super().form_valid(form)


class ListingClose(View):
    model = Listing
    template_name = "auctions/listing_close.html"

    def get(self, request, id):
        listing = get_object_or_404(self.model, pk=id)
        if listing.author == request.user:
            winner = listing.user_with_max_bid
            return render(request, self.template_name, {
                "listing": listing,
                "winner": winner,
            })
        raise PermissionDenied

    def post(self, request, id):
        listing = get_object_or_404(Listing, pk=id)
        listing.active = False
        listing.save()
        return redirect("index")


class WatchlistDetail(LoginRequiredMixin, CustomPageRangeMixin, ListView):
    context_object_name = "listings"
    login_url = "login"
    paginate_by = 6
    template_name = "auctions/watchlist.html"

    def get_queryset(self):
        listings = self.request.user.watchlist_listings.all()
        return listings