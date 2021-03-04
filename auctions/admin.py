from django.contrib import admin
from .models import User, Auction, Bid, Comment

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "password")

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "category", "description", "initial_bid")
    filter_horizontal = ("watchlist_users",)

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "bid", "auction")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "auction")

# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)