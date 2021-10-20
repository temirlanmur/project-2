from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, View
from django.core.exceptions import PermissionDenied

from .models import User, ListingCategory, Listing
from .forms import UserForm, ListingCategoryForm, ListingForm, CommentForm, BidForm
from .utils import ConstructListMixin


class ListingList(ListView):
    context_object_name = "listings"
    paginate_by = 6    
    template_name = "auctions/index.html"

    pages_on_each_side = 1  # The number of pages on each side of the current page number

    def get_queryset(self):
        active_listings = Listing.objects.filter(active=True)
        return active_listings
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add custom page range to the context. (For pagination)
        page_number = context['page_obj'].number
        num_pages = context['paginator'].num_pages

        left_index = int(page_number) - self.pages_on_each_side
        if left_index < 1:
            left_index = 1
        right_index = int(page_number) + self.pages_on_each_side
        if right_index > num_pages:
            right_index = num_pages
        custom_range = range(left_index, right_index + 1)  # Because python range(1, 4) is from 1 till 3
        
        context['custom_page_range'] = custom_range
        return context


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


class CategoryDetail(ListView):
    context_object_name = 'listings'
    paginate_by = 6
    template_name = "auctions/category_detail.html"

    pages_on_each_side = 1  # The number of pages on each side of the current page number
    
    def get_queryset(self):
        category = get_object_or_404(ListingCategory, slug=self.kwargs['slug'])
        listings = category.listings.filter(active=True)
        return listings
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add custom page range to the context. (For pagination)
        page_number = context['page_obj'].number
        num_pages = context['paginator'].num_pages

        left_index = int(page_number) - self.pages_on_each_side
        if left_index < 1:
            left_index = 1
        right_index = int(page_number) + self.pages_on_each_side
        if right_index > num_pages:
            right_index = num_pages
        custom_range = range(left_index, right_index + 1)  # Because python range(1, 4) is from 1 till 3
        
        context['custom_page_range'] = custom_range
        return context


class CategoryCreate(View):
    form_class = ListingCategoryForm
    template_name = "auctions/category_create.html"

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, self.template_name, {
                "form": self.form_class()
            })
        return HttpResponse('Unauthorized', status=401)

    def post(self,request):
        if request.user.is_authenticated:
            bound_form = self.form_class(request.POST)        
            if bound_form.is_valid():
                new_category = bound_form.save()
                return redirect(new_category)        
            else:
                return render(request, self.template_name, {
                    "form": bound_form
                })
        return HttpResponse('Unauthorized', status=401)


class ListingDetail(View):
    model = Listing              
    template_name = "auctions/listing_detail.html"

    def get(self, request, id):
        listing = get_object_or_404(self.model, pk=id)        
        isauthor_flag = (request.user == listing.author)
        inwatchlist_flag = listing.watchlisted_by.filter(username=request.user)
        return render(request, self.template_name, {
            "listing": listing,
            "isauthor_flag": isauthor_flag,
            "inwatchlist_flag": inwatchlist_flag,
            "bid_form": BidForm(),
            "comment_form": CommentForm()            
        })
    
    def post(self, request, id):
        listing = get_object_or_404(self.model, pk=id)
        isauthor_flag = (request.user == listing.author)
        inwatchlist_flag = listing.watchlisted_by.filter(username=request.user)
        bidlow_flag = False
        bid_form = BidForm()
        comment_form = CommentForm()
        # Process watchlist
        if "addtowatchlist" in request.POST:            
            if inwatchlist_flag:
                listing.watchlisted_by.remove(request.user)
                inwatchlist_flag = False                   
            else:
                listing.watchlisted_by.add(request.user)
                inwatchlist_flag = True
        # Process bid
        if "makebid" in request.POST:
            bid_form = BidForm(request.POST)                
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
        if "addcomment" in request.POST:            
            comment_form = CommentForm(request.POST)   
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.author = request.user
                new_comment.on_listing = listing
                new_comment.save()
                comment_form = CommentForm()        
        return render(request, self.template_name, {
            "listing": listing,
            "isauthor_flag": isauthor_flag,
            "inwatchlist_flag": inwatchlist_flag,
            "bidlow_flag": bidlow_flag,
            "bid_form": bid_form,
            "comment_form": comment_form
        })


class ListingUpdate(View):
    model = Listing    
    form_class = ListingForm
    template_name = "auctions/listing_update.html"

    def get(self, request, id):
        listing = get_object_or_404(self.model, pk=id)
        form = self.form_class(instance=listing)
        form.disable_starting_bid()
        if listing.author == request.user:
            return render(request, self.template_name, {
                "listing": listing,
                "form": form
            })
        raise PermissionDenied
    

    def post(self, request, id):
        listing = get_object_or_404(Listing, pk=id)
        if listing.author == request.user:
            data = request.POST.dict()
            data["starting_bid"] = listing.starting_bid
            update_form = self.form_class(data, instance=listing)
            if update_form.is_valid():                
                updated_listing = update_form.save()
                return redirect(updated_listing)
            else:
                return render(request, self.template_name, {
                    "listing": listing,
                    "form": update_form
                })
        raise PermissionDenied        


class ListingCreate(View):  
    model = Listing
    form_class = ListingForm  
    template_name = "auctions/listing_create.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, self.template_name, {
                "form": self.form_class()
            })
        return HttpResponse('Unauthorized', status=401)
    
    def post(self, request):
        bound_form = self.form_class(request.POST)
        if request.user.is_authenticated:
            if bound_form.is_valid():
                new_listing = bound_form.save(commit=False)
                new_listing.author=request.user
                new_listing.save()
                return redirect(new_listing)
            else:
                return render(request, self.template_name, {
                    "form": bound_form
                })
        return HttpResponse('Unauthorized', status=401)


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


class WatchlistDetail(ConstructListMixin, View):
    model = User
    template_name = "auctions/watchlist.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            watchlist = request.user.watchlist_listings.all()
            return render(request, self.template_name, {
                "construct_list": self.construct_list(watchlist)
            })
        return HttpResponse('Unauthorized', status=401)