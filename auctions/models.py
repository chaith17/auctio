# auctions/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class UserProfile(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    vendues_created = models.PositiveIntegerField(default=0)
    tenders_placed = models.PositiveIntegerField(default=0)
    auctions_won = models.PositiveIntegerField(default=0)

class Auction(models.Model):
    CATEGORY_CHOICES = [
        ("Other", "Other"),
        ("Art", "Art"),
        ("Electronics", "Electronics"),
        ("Furniture", "Furniture"),
        ("Collectible", "Collectible"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="auctions")
    image = models.ImageField(upload_to="auctions/", null=True, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="Other")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def current_bid(self):
        latest = self.bids.order_by("-amount").first()
        return latest.amount if latest else self.base_price

    @property
    def time_remaining_seconds(self):
        delta = self.ends_at - timezone.now()
        return int(delta.total_seconds()) if delta.total_seconds() > 0 else 0


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}"


class Notification(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


class Vendue(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    duration_minutes = models.PositiveIntegerField(default=60)
    category = models.CharField(max_length=100, default="Other")
    attachment = models.ImageField(upload_to='vendue_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
