# auctio/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from auctions.consumers import AuctionConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auctio.settings")
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": URLRouter(
            [
                path("ws/auction/<int:auction_id>/", AuctionConsumer.as_asgi()),
            ]
        ),
    }
)
