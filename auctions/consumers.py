# auctions/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Auction, Bid, Notification, UserProfile
from django.utils import timezone

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope["url_route"]["kwargs"]["auction_id"]
        self.group_name = f"auction_{self.auction_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        if action == "place_bid":
            amount = data.get("amount")
            user_id = data.get("user_id")
            result = await sync_to_async(self.place_bid)(user_id, amount)
            if result:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "bid_message",
                        "bidder": result["bidder"],
                        "amount": str(result["amount"]),
                        "created_at": result["created_at"],
                    },
                )

    async def bid_message(self, event):
        await self.send(text_data=json.dumps(event))

    def place_bid(self, user_id, amount):
        try:
            auction = Auction.objects.get(pk=self.auction_id)
            user = UserProfile.objects.get(pk=user_id)
            amount_dec = float(amount)
            current = float(auction.current_bid)
            if amount_dec > current:
                b = Bid.objects.create(auction=auction, bidder=user, amount=amount_dec)
                user.tenders_placed += 1
                user.save()
                # Optionally create notification for owner when outbid
                Notification.objects.create(
                    user=auction.owner,
                    message=f"{user.username} placed a bid of ₹{amount_dec} on {auction.title}",
                )
                return {"bidder": user.username, "amount": amount_dec, "created_at": b.created_at.isoformat()}
        except Exception:
            return None
