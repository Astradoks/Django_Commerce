from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Auction, Bid, Comment, User

class CommentForm(forms.Form):
    comment = forms.CharField(label="Write a comment here:", widget=forms.Textarea(attrs={'class': 'form-control'}))

class CreateAuctionForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label="Write the product description here:", widget=forms.Textarea(attrs={'class': 'form-control'}))
    initial_bid = forms.DecimalField(decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    image = forms.CharField(label="Enter here a url for the product image if you want", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.CharField(label="Write a category for this product if you want", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

def index(request):
    all_auctions = [x for x in Auction.objects.filter(active=True)]
    prices = []
    for auction in all_auctions:
        prices.append(max([x.bid for x in auction.auction_bids.all()]))
    return render(request, "auctions/index.html", {
        "all_auctions": tuple(zip(all_auctions, prices))
    })

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

def categories(request):
    if request.method == "POST":
        category = request.POST["category"]
        filtered_auctions = Auction.objects.filter(category=category, active=True)
        prices = []
        for auction in filtered_auctions:
            prices.append(max([x.bid for x in auction.auction_bids.all()]))
        return render(request, "auctions/filtered_category.html", {
            "filtered_auctions": tuple(zip(filtered_auctions, prices)),
            "category": category
        })
    repeat_categoies = [x.category for x in Auction.objects.filter(active=True)]
    categories = []
    for x in repeat_categoies:
        if x not in categories:
            categories.append(x)
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def auction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    max_bid = max([x.bid for x in auction.auction_bids.all()])
    max_buyer = Bid.objects.filter(bid=max_bid).first().user
    comments = Comment.objects.filter(auction=auction)
    in_watchlist = False
    possible_close = False
    if request.user.is_authenticated:
        user_watchlist = request.user.watchlist.all()
        user_watchlist = [x.id for x in user_watchlist]
        in_watchlist = auction_id in user_watchlist
        possible_close = auction.user == request.user
    return render(request, "auctions/auction.html", {
        "auction": auction,
        "max_bid": max_bid,
        "max_buyer": max_buyer,
        "logged_user": request.user,
        "comment_form": CommentForm(),
        "comments": comments,
        "in_watchlist": in_watchlist,
        "possible_close": possible_close
    })

@login_required(login_url="login")
def active(request):
    if request.method == "POST":
        auction_id = request.POST["auction_id"]
        auction = Auction.objects.get(id=auction_id)
        auction.active = False
        auction.save()
    return HttpResponseRedirect(reverse("auction", args=[auction_id]))

@login_required(login_url="login")
def bid(request):
    auction_id = request.POST["auction_id"]
    auction = Auction.objects.get(id=auction_id)
    max_bid = max([x.bid for x in auction.auction_bids.all()])
    max_buyer = Bid.objects.filter(bid=max_bid).first().user
    message = ""
    message_category = ""
    comments = Comment.objects.filter(auction=auction)
    user_watchlist = request.user.watchlist.all()
    user_watchlist = [x.id for x in user_watchlist]
    in_watchlist = auction_id in user_watchlist
    possible_close = auction.user = request.user
    if request.method == "POST":
        bid = request.POST["bid"]
        try:
            bid = float(bid)
            if bid > max_bid:
                bid = Bid(user=request.user, bid=bid, auction=auction)
                bid.save()
                message = "Bid was accepted"
                message_category = "success"
            else:
                message = "Bid was not accepted!"
                message_category = "danger"
        except:
            message = "Bid was not accepted!"
            message_category = "danger"
    return render(request, "auctions/auction.html", {
        "auction": auction,
        "max_bid": max_bid,
        "max_buyer": max_buyer,
        "message": message,
        "message_category": message_category,
        "logged_user": request.user,
        "comment_form": CommentForm(),
        "comments": comments,
        "in_watchlist": in_watchlist,
        "possible_close": possible_close
    })

@login_required(login_url="login")
def comment(request):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.cleaned_data["comment"]
            user = request.user
            auction_id = request.POST["auction_id"]
            auction = Auction.objects.get(id=auction_id)
            comment = Comment(user= user, auction=auction, comment=comment)
            comment.save()
    return HttpResponseRedirect(reverse("auction", args=[auction_id]))

@login_required(login_url="login")
def watchlist(request):
    user_watchlist = request.user.watchlist.all()
    watchlist_auctions = [x for x in user_watchlist]
    user_watchlist = [x.id for x in user_watchlist]
    prices = []
    for auction in watchlist_auctions:
        prices.append(max([x.bid for x in auction.auction_bids.all()]))
    if request.method == "POST":
        auction_id = request.POST["auction_id"]
        auction = Auction.objects.get(id=auction_id)
        in_watchlist = int(auction_id) in user_watchlist
        if in_watchlist:
            auction.watchlist_users.remove(request.user)
        else:
            auction.watchlist_users.add(request.user)
        return HttpResponseRedirect(reverse("auction", args=[auction_id]))
    return render(request, "auctions/watchlist.html", {
        "watchlist_auctions": tuple(zip(watchlist_auctions, prices))
    })

@login_required(login_url="login")
def create(request):
    if request.method == "POST":
        create_form = CreateAuctionForm(request.POST)
        if create_form.is_valid():
            title = create_form.cleaned_data["title"]
            description = create_form.cleaned_data["description"]
            initial_bid = create_form.cleaned_data["initial_bid"]
            image = create_form.cleaned_data["image"]
            category = create_form.cleaned_data["category"]
            if image == "":
                image = "https://st3.depositphotos.com/23594922/31822/v/600/depositphotos_318221368-stock-illustration-missing-picture-page-for-website.jpg"
            if category == "":
                category = "No category"
            auction = Auction(user = request.user, title = title, category = category, description = description, image = image, initial_bid = initial_bid)
            auction.save()
            bid = Bid(user = request.user, bid= initial_bid, auction = auction)
            bid.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "create_form": create_form
            })
    return render(request, "auctions/create.html", {
        "create_form": CreateAuctionForm()
    })