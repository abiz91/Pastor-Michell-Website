import uuid

import requests
import stripe
from django.contrib.auth import login
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import RegistrationForm

User = get_user_model()


def home(request):
    return render(request, "home1.html",)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(
            request,
            "Welcome to Matriarch Mantle. Your account has been created.",
        )
        return redirect("home")

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    purchases = Purchase.objects.filter(
        user=request.user,
        status=Purchase.Status.PAID,
    )
    services = Service.objects.filter(active=True)
    return render(
        request,
        "dashboard.html",
        {"purchases": purchases, "services": services},
    )


@login_required
def booking(request):
    services = Service.objects.filter(active=True)
    purchases = Purchase.objects.filter(
        user=request.user,
        status=Purchase.Status.PAID,
    )
    return render(
        request,
        "Booking.html",
        {"purchases": purchases, "services": services},
    )


@login_required
def checkout(request, service_id, provider):
    if request.method != "POST":
        return redirect("booking")

    if provider not in ("stripe", "paystack"):
        messages.error(request, "Invalid payment provider.")
        return redirect("booking")

    service = get_object_or_404(Service, pk=service_id, active=True)
    reference = uuid.uuid4().hex

    purchase = Purchase.objects.create(
        user=request.user,
        service=service,
        provider=provider,
        reference=reference,
    )

    try:
        if provider == "stripe":
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[{
                    "price_data": {
                        "currency": service.currency.lower(),
                        "product_data": {"name": service.name},
                        "unit_amount": int(service.amount * 100),
                    },
                    "quantity": 1,
                }],
                success_url=(
                    settings.SITE_URL
                    + reverse("stripe_success")
                    + "?session_id={CHECKOUT_SESSION_ID}"
                ),
                cancel_url=settings.SITE_URL + reverse("booking"),
                metadata={"purchase_id": str(purchase.pk)},
            )
            purchase.reference = session.id
            purchase.save(update_fields=["reference"])
            return redirect(session.url)

        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers={
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "email": request.user.email,
                "amount": int(service.amount * 100),
                "currency": service.currency.upper(),
                "reference": reference,
                "callback_url": (
                    settings.SITE_URL + reverse("paystack_callback")
                ),
            },
            timeout=20,
        )
        data = response.json()
        if response.ok and data.get("status") and data.get("data", {}).get("authorization_url"):
            return redirect(data["data"]["authorization_url"])

    except (requests.RequestException, stripe.error.StripeError, ValueError) as exc:
        messages.error(request, f"Payment could not be started: {exc}")
    except Exception:
        messages.error(request, "Payment could not be started. Please try again.")

    purchase.delete()
    return redirect("booking")


@login_required
def stripe_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "Missing Stripe checkout session.")
        return redirect("booking")

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        messages.error(request, "Unable to verify the Stripe payment.")
        return redirect("booking")

    if session.payment_status == "paid":
        Purchase.objects.filter(
            reference=session.id,
            user=request.user,
        ).update(status=Purchase.Status.PAID)
        return redirect("whatsapp")

    messages.error(request, "Payment has not been completed.")
    return redirect("booking")


def paystack_callback(request):
    reference = request.GET.get("reference")
    if not reference:
        messages.error(request, "Missing Paystack payment reference.")
        return redirect("booking")

    purchase = get_object_or_404(Purchase, reference=reference)

    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
            timeout=20,
        )
        data = response.json()
    except (requests.RequestException, ValueError):
        messages.error(request, "Unable to verify the Paystack payment.")
        return redirect("booking")

    payment_data = data.get("data", {})
    if (
        response.ok
        and data.get("status")
        and payment_data.get("status") == "success"
        and payment_data.get("reference") == reference
    ):
        purchase.status = Purchase.Status.PAID
        purchase.save(update_fields=["status"])
        return redirect("login")

    messages.error(request, "Payment could not be verified.")
    return redirect("login")


@csrf_exempt
def stripe_webhook(request):
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.headers.get("Stripe-Signature"),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest("Invalid Stripe webhook.")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        if session.get("payment_status") == "paid":
            Purchase.objects.filter(
                reference=session["id"]
            ).update(status=Purchase.Status.PAID)

    return HttpResponse(status=200)


@login_required
def whatsapp(request):
    has_paid_purchase = Purchase.objects.filter(
        user=request.user,
        status=Purchase.Status.PAID,
    ).exists()

    if not has_paid_purchase:
        return redirect("dashboard")

    number = settings.WHATSAPP_NUMBER
    return redirect(
        f"https://wa.me/{number}"
        "?text=Bonjour%20MarcMind%2C%20je%20viens%20de%20m%27inscrire."
    )


def nigeria(request):
    return render(request, "nigeria.html")


def ethiopia(request):
    return render(request, "ethiopia.html")

def kenya(request):
    return render(request, "kenya.html")


@login_required
def mentorship(request):
    return render(request, "mentorship.html")

def library(request):
    return render(request, "gallery.html")
def gallery2(request):
    return render(request, "gallery2.html")
