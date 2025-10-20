import os
import uuid
import stripe
from dataclasses import dataclass
from typing import Optional
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@dataclass
class CheckoutResult:
    url: str
    session_id: str
    price_id: str
    product_id: str


def _idem_key(user_id: int, course_id: int, amount_cents: int) -> str:
    src = f"user:{user_id}|course:{course_id}|amount:{amount_cents}"
    return f"lms-{uuid.uuid5(uuid.NAMESPACE_DNS, src)}"


def create_checkout_session(
    *,
    course_name: str,
    course_id: int,
    user_email: Optional[str],
    user_id: int,
    amount_cents: int,
    currency: str = "usd",
) -> CheckoutResult:

    product = stripe.Product.create(
        name=course_name,
        metadata={"course_id": str(course_id)},
        idempotency_key=_idem_key(user_id, course_id, amount_cents) + ":product",
    )

    price = stripe.Price.create(
        unit_amount=amount_cents,
        currency=currency,
        product=product.id,
        idempotency_key=_idem_key(user_id, course_id, amount_cents) + ":price",
    )

    success_url = settings.STRIPE_SUCCESS_URL
    cancel_url = settings.STRIPE_CANCEL_URL

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price.id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=user_email,
        idempotency_key=_idem_key(user_id, course_id, amount_cents) + ":session",
    )

    return CheckoutResult(
        url=session.url, session_id=session.id, price_id=price.id, product_id=product.id
    )
