from django import forms
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.text import slugify

from .models import User, ListingCategory, Listing, Bid, Comment


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",            
            "avatar"
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your first name"                
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your last name"                
            }),
            "avatar": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Paste the link for your avatar image"                
            })
        }
        

class ListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "category",            
            "image",
            "starting_bid"
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Title"                
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Description",
                "rows": "2"               
            }),
            "category": forms.Select(attrs={
                "class": "form-select",
                "placeholder": "Choose one"                
            }),
            "starting_bid": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter digits, i.e. '50'"                
            }),
            "image": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Paste your image link here"                
            })
        }
    
    def disable_starting_bid(self):            
        self.fields["starting_bid"].widget.attrs["readonly"] = True
    

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]
        widgets = {
            "amount": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your bid"                
            })
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "What do you think?"                
            }),
        }