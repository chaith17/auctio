# auctions/views.py
from decimal import Decimal, InvalidOperation
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from .models import Auction, Bid, Notification, Vendue, UserProfile
from .utils import process_expired_auctions

from .forms import VendueForm, RegisterForm
from django.contrib.auth import login, authenticate, logout

def home(request):
    return render(request, "auctions/home.html")


@login_required(login_url='/login/')
def listing(request):
    process_expired_auctions()
    qs = Auction.objects.filter(is_active=True)

    cat = request.GET.get("category")
    if cat:
        qs = qs.filter(category=cat)

    pmin = request.GET.get("price_min")
    pmax = request.GET.get("price_max")

    if pmin:
        qs = qs.filter(base_price__gte=pmin)
    if pmax:
        qs = qs.filter(base_price__lte=pmax)

    return render(request, "auctions/listing.html", {"auctions": qs})


@login_required(login_url='/login/')
def detail(request, pk):
    process_expired_auctions()
    auction = get_object_or_404(Auction, pk=pk)

    # Handle POST = placing a bid
    if request.method == "POST" and request.user.is_authenticated:
        # Prevent owner from bidding on their own auction
        if auction.owner == request.user:
            messages.error(request, "You cannot bid on your own auction.")
            return redirect("auctions:detail", pk=pk)

        raw_amount = request.POST.get("amount")
        if not raw_amount:
            messages.error(request, "Please enter a bid amount.")
            return redirect("auctions:detail", pk=pk)

        try:
            amount = Decimal(raw_amount)
        except (InvalidOperation, ValueError):
            messages.error(request, "Invalid bid amount.")
            return redirect("auctions:detail", pk=pk)

        # ensure auction is still active and hasn't ended
        if not auction.is_active or auction.time_remaining_seconds <= 0:
            messages.error(request, "This auction is no longer active.")
            return redirect("auctions:detail", pk=pk)

        current = Decimal(auction.current_bid)
        # require strictly greater than current bid
        if amount <= current:
            messages.error(request, f"Your bid must be greater than the current bid (₹{current}).")
            return redirect("auctions:detail", pk=pk)

        # create and save bid
        bid = Bid(auction=auction, bidder=request.user, amount=amount)
        bid.save()

        # optional: increment quick counter on user profile (keeps an at-a-glance stat)
        # increment tenders_placed atomically
        if isinstance(request.user, UserProfile):
            from django.db.models import F
            UserProfile.objects.filter(pk=request.user.pk).update(tenders_placed=F("tenders_placed") + 1)

        messages.success(request, f"Bid placed: ₹{amount} — good luck!")
        return redirect("auctions:detail", pk=pk)

    # GET -> show detail page
    return render(request, "auctions/detail.html", {"auction": auction})


@login_required(login_url='/login/')
def bids(request):
    # show bids created by the logged-in user with auction info
    participated = request.user.bids.select_related("auction").order_by("-created_at")
    return render(request, "auctions/bids.html", {"bids": participated})


@login_required(login_url='/login/')
def vendue(request):
    if request.method == "POST":
        form = VendueForm(request.POST, request.FILES)
        if form.is_valid():
            vendue = form.save(commit=False)
            vendue.seller = request.user
            vendue.save()

            # optional quick counter
            # increment vendues_created atomically
            if isinstance(request.user, UserProfile):
                from django.db.models import F
                UserProfile.objects.filter(pk=request.user.pk).update(vendues_created=F("vendues_created") + 1)

            # Create Auction from Vendue
            ends_at = timezone.now() + timedelta(minutes=vendue.duration_minutes)

            auction = Auction.objects.create(
                title=vendue.title,
                description=vendue.description,
                base_price=vendue.base_price,
                owner=request.user,
                category=vendue.category,
                ends_at=ends_at,
                image=vendue.attachment
            )

            messages.success(request, "Auction created successfully.")
            return redirect("auctions:listing")
    else:
        form = VendueForm()

    return render(request, "auctions/vendue.html", {"form": form})


@login_required(login_url='/login/')
def alerts(request):
    process_expired_auctions()
    notes = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "auctions/alerts.html", {"notifications": notes})


@login_required(login_url='/login/')
def account(request):
    """
    Shows user stats from persisted counters.
    """
    process_expired_auctions()
    user = request.user

    context = {
        "vendues_created": user.vendues_created,
        "tenders_placed": user.tenders_placed,
        "auctions_won": user.auctions_won,
    }
    return render(request, "auctions/account.html", context)


def user_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("auctions:home")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "auctions/login.html")


def user_register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("auctions:home")
    else:
        form = RegisterForm()

    return render(request, "auctions/register.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("auctions:login")


@login_required(login_url='/login/')
def auction_delete(request, pk):
    """
    Delete an auction. Only the auction owner can delete.
    Only accepts POST (prevents accidental deletes via GET).
    """
    auction = get_object_or_404(Auction, pk=pk)

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # only owner can delete
    if auction.owner != request.user:
        messages.error(request, "You are not allowed to delete this auction.")
        return HttpResponseForbidden("Forbidden")

    auction.delete()
    messages.success(request, "Auction removed.")
    return redirect("auctions:listing")
