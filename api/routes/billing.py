"""Stripe billing: checkout, portal, webhooks."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.auth import CurrentUser
from api.db import get_db
from api.models import User, UserPlan
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def _get_stripe():
    """Lazy import to avoid failure when stripe not installed."""
    try:
        import stripe
        return stripe
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured. Install stripe and set STRIPE_SECRET_KEY.",
        )


async def _get_or_create_stripe_customer(db: AsyncSession, user: User) -> str:
    """Get existing Stripe customer ID or create one."""
    from api.config import settings

    if user.stripe_customer_id:
        return user.stripe_customer_id

    stripe = _get_stripe()
    stripe.api_key = settings.stripe_secret_key
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured.",
        )

    customer = stripe.Customer.create(email=user.email, metadata={"user_id": user.id})
    user.stripe_customer_id = customer.id
    await db.commit()
    return customer.id


def _price_id_for_plan(plan: str):
    """Return Stripe price ID for plan. plan='starter' or 'pro'."""
    from api.config import settings
    if plan == "starter" and settings.stripe_price_id_starter:
        return settings.stripe_price_id_starter
    if plan == "pro" and settings.stripe_price_id_pro:
        return settings.stripe_price_id_pro
    return None


@router.post("/create-checkout-session")
async def create_checkout_session(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    plan: str = "pro",
):
    """Create Stripe Checkout session for Starter or Pro subscription. Returns URL to redirect user."""
    from api.config import settings

    price_id = _price_id_for_plan(plan)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Plan '{plan}' not configured. Set STRIPE_PRICE_ID_{plan.upper()}.",
        )

    stripe = _get_stripe()
    stripe.api_key = settings.stripe_secret_key
    customer_id = await _get_or_create_stripe_customer(db, user)

    base = settings.portal_base_url.rstrip("/")
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{base}/dashboard?success=true&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{base}/dashboard?canceled=true",
        metadata={"user_id": user.id, "plan": plan},
    )
    return {"url": session.url}


@router.post("/create-portal-session")
async def create_portal_session(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create Stripe Customer Portal session. Returns URL for managing payment methods and subscription."""
    from api.config import settings

    stripe = _get_stripe()
    stripe.api_key = settings.stripe_secret_key
    customer_id = await _get_or_create_stripe_customer(db, user)

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{settings.portal_base_url.rstrip('/')}",
    )
    return {"url": session.url}


@router.post("/sync-subscription")
async def sync_subscription(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Sync plan from Stripe subscriptions. Use when webhook didn't update the plan."""
    from api.config import settings

    stripe = _get_stripe()
    stripe.api_key = settings.stripe_secret_key
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured.",
        )

    customer_id = user.stripe_customer_id
    if not customer_id:
        # Try to find customer by email (e.g. if they paid via Payment Link)
        customers = stripe.Customer.list(email=user.email, limit=1)
        if customers.data:
            customer_id = customers.data[0].id
            user.stripe_customer_id = customer_id
            await db.commit()

    if not customer_id:
        return {"message": "No Stripe customer linked.", "plan": user.plan or "free"}

    subs = stripe.Subscription.list(
        customer=customer_id,
        status="active",
        limit=10,
        expand=["data.items.data.price"],
    )
    if subs.data:
        user.plan = _plan_from_subscription(subs.data[0], settings)
        await db.commit()
        return {"message": "Subscription synced.", "plan": user.plan}
    user.plan = UserPlan.FREE.value
    await db.commit()
    return {"message": "No active subscription found.", "plan": "free"}


def _plan_from_subscription(sub, settings) -> str:
    """Determine plan from subscription line items (Starter or Pro price ID)."""
    items = sub.get("items", {})
    if isinstance(items, dict):
        items = items.get("data", [])
    for item in items:
        price = item.get("price")
        price_id = price if isinstance(price, str) else (price.get("id") if isinstance(price, dict) else getattr(price, "id", None))
        if not price_id:
            continue
        if settings.stripe_price_id_starter and price_id == settings.stripe_price_id_starter:
            return UserPlan.STARTER.value
        if settings.stripe_price_id_pro and price_id == settings.stripe_price_id_pro:
            return UserPlan.PRO.value
    return UserPlan.PRO.value  # Default to Pro for unknown prices


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks. Updates user plan on subscription events."""
    from api.config import settings
    from api.db import async_session_maker

    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    stripe = _get_stripe()
    stripe.api_key = settings.stripe_secret_key

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook signature verification failed: {e}")

    async with async_session_maker() as db:
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session.get("metadata", {}).get("user_id")
            plan = session.get("metadata", {}).get("plan", "pro")
            if user_id:
                result = await db.execute(select(User).where(User.id == user_id))
                u = result.scalar_one_or_none()
                if u:
                    sub_id = session.get("subscription")
                    if sub_id:
                        sub = stripe.Subscription.retrieve(sub_id, expand=["items.data.price"])
                        u.plan = _plan_from_subscription(sub, settings)
                    else:
                        u.plan = UserPlan.STARTER.value if plan == "starter" else UserPlan.PRO.value
                    await db.commit()

        elif event["type"] == "customer.subscription.created":
            sub = event["data"]["object"]
            customer_id = sub.get("customer")
            if customer_id:
                result = await db.execute(
                    select(User).where(User.stripe_customer_id == customer_id)
                )
                u = result.scalar_one_or_none()
                if u:
                    u.plan = _plan_from_subscription(sub, settings)
                    await db.commit()

        elif event["type"] == "customer.subscription.deleted":
            sub = event["data"]["object"]
            customer_id = sub.get("customer")
            if customer_id:
                result = await db.execute(
                    select(User).where(User.stripe_customer_id == customer_id)
                )
                u = result.scalar_one_or_none()
                if u:
                    u.plan = UserPlan.FREE.value
                    await db.commit()

    return {"received": True}
