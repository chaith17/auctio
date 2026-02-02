from django.utils import timezone
from django.db import transaction, models
from .models import Auction, Bid, Notification, UserProfile

def process_expired_auctions():
    """
    Checks for active auctions that have passed their end time.
    Closes them (sets is_active=False), determines the winner,
    sends notifications, and updates user stats.
    """
    now = timezone.now()
    # Filter for active auctions that have expired
    expired_auctions = Auction.objects.filter(is_active=True, ends_at__lt=now)

    for auction in expired_auctions:
        # Use atomic transaction to ensure data integrity
        with transaction.atomic():
            # Re-fetch the auction to ensure strict consistency (lock logic available if using select_for_update)
            # For this simple case, checking is_active again after lock or just here is safer.
            # Using select_for_update would be better for high concurrency, but let's stick to simple safe logic first.
            # We want to lock this row.
            curr_auction = Auction.objects.select_for_update().filter(pk=auction.pk).first()
            
            if not curr_auction or not curr_auction.is_active:
                continue

            # Mark as inactive/completed
            curr_auction.is_active = False
            curr_auction.save()

            # Determine the highest bidder
            highest_bid = curr_auction.bids.order_by("-amount").first()

            if highest_bid:
                winner = highest_bid.bidder
                winning_amount = highest_bid.amount

                # 1. Update Winner's "Won" stat
                # We also lock the user row to safely increment
                UserProfile.objects.filter(pk=winner.pk).update(auctions_won=models.F('auctions_won') + 1)
                
                # 2. Send "You won" alert
                Notification.objects.create(
                    user=winner,
                    message=f"You won the auction '{curr_auction.title}' with a bid of {winning_amount}!"
                )

                # 3. Send "You lost" alerts to other unique bidders
                # Find all other bidders
                loser_ids = curr_auction.bids.exclude(bidder=winner).values_list('bidder', flat=True).distinct()
                
                # Bulk create notifications might be more efficient, but let's loop for simplicity
                notifications = []
                for uid in loser_ids:
                    notifications.append(Notification(
                        user_id=uid,
                        message=f"You lost the auction '{curr_auction.title}'."
                    ))
                
                if notifications:
                    Notification.objects.bulk_create(notifications)
            
            else:
                # No bids were placed.
                # Auction closes without a winner.
                pass
