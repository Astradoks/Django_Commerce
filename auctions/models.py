from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="auctions", null=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    image = models.CharField(max_length=255, null=True)
    initial_bid = models.DecimalField(decimal_places=2, max_digits=6, null=True)
    watchlist_users = models.ManyToManyField(User, blank=True, related_name="watchlist")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user}: {self.title}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_bids", null=True)
    bid = models.DecimalField(decimal_places=2, max_digits=6)
    auction = models.ForeignKey(Auction, on_delete=models.PROTECT, related_name="auction_bids")

    def __str__(self):
        return f"{self.auction}: {self.bid}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_comments", null=True)
    auction = models.ForeignKey(Auction, on_delete=models.PROTECT, related_name="auction_comments")
    comment = models.TextField()

    def __str__(self):
        return f"{self.auction}: {self.comment}"

