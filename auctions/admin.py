# auctions/admin.py
from django.contrib import admin
from .models import UserProfile, Auction, Bid, Notification
from django.contrib.auth.admin import UserAdmin

@admin.register(UserProfile)
class CustomUserAdmin(UserAdmin):
    model = UserProfile
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("avatar", "vendues_created", "tenders_placed", "auctions_won")}),
    )

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "base_price", "ends_at", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title", "description")

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("auction", "bidder", "amount", "created_at")
    list_filter = ("auction",)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "read")
