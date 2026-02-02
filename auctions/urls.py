# auctions/urls.py
from django.urls import path
from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.home, name="home"),
    path("listing/", views.listing, name="listing"),
    path("auction/<int:pk>/", views.detail, name="detail"),
    path("auction/<int:pk>/delete/", views.auction_delete, name="auction_delete"),
    path("bids/", views.bids, name="bids"),
    path("vendue/", views.vendue, name="vendue"),
    path("alerts/", views.alerts, name="alerts"),
    path("account/", views.account, name="account"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.user_register, name="register"),
]
