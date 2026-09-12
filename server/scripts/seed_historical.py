"""
Seed Historical Data — Generates 30 days of realistic baseline ticket data.

Simulates the fictitious company "CloudFlow Analytics" with realistic
circadian patterns, category distributions, and sentiment variations.

Usage:
    python -m scripts.seed_historical
"""
import random
import uuid
import sys
import os
import math
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import sync_engine, SyncSessionLocal, Base
from app.models import Ticket, Cluster, BaselineMetric
from app.services.embedding_service import embedding_service
from app.services.sentiment_service import compute_sentiment

from sqlalchemy import text

# --- Configuration ---
DAYS_OF_HISTORY = 30
TICKETS_PER_DAY_AVG = 280  # ~8400 total

CATEGORIES = {
    "login": {
        "weight": 0.18,
        "messages": [
            "I forgot my password and the reset link doesn't work.",
            "Can't log in after changing my email address.",
            "Getting 'account not found' when trying to sign in.",
            "Two-factor authentication is not sending me the code.",
            "Login page is loading very slowly today.",
            "My session keeps expiring every 5 minutes.",
            "I get redirected back to login after entering credentials.",
            "SSO login with my company account is failing.",
            "New employee can't create an account. Registration error.",
            "Password requirements are too strict, can't set a new one.",
            "Having trouble signing in on my phone.",
            "Account says it's locked but I haven't failed any login attempts.",
            "Can I change my login email address?",
            "The 'remember me' option doesn't seem to work.",
            "Getting a CAPTCHA error on the login page.",
        ],
    },
    "payments": {
        "weight": 0.15,
        "messages": [
            "My credit card payment was declined but I have sufficient funds.",
            "I was charged the wrong amount for my order.",
            "Payment confirmation email never arrived.",
            "Can I pay with PayPal instead of credit card?",
            "The payment page keeps timing out.",
            "I see a pending charge but my order wasn't confirmed.",
            "My invoice doesn't match what I actually ordered.",
            "Can I get a receipt for my last purchase?",
            "Payment went through twice for the same order.",
            "International payment is being blocked by your system.",
            "How do I update my payment method?",
            "The coupon code isn't applying the correct discount at checkout.",
            "Bank transfer option is not available in my country.",
            "Getting 'payment processing error' when trying to check out.",
            "I need to split payment between two cards.",
        ],
    },
    "checkout": {
        "weight": 0.10,
        "messages": [
            "Items disappear from my cart when I try to check out.",
            "The checkout button is grayed out and I can't click it.",
            "Shipping options aren't showing during checkout.",
            "I can't apply my promo code at checkout.",
            "The page refreshes and clears my cart at checkout step.",
            "Checkout is stuck on 'processing' for 10 minutes.",
            "I can't change the shipping address during checkout.",
            "Tax calculation seems wrong on my order.",
            "Can't select my preferred delivery date at checkout.",
            "The checkout flow is confusing, too many steps.",
        ],
    },
    "refunds": {
        "weight": 0.08,
        "messages": [
            "I requested a refund 2 weeks ago and haven't received it.",
            "How long does a refund take to process?",
            "I was refunded the wrong amount.",
            "Can I get a refund for a subscription I cancelled?",
            "Refund was approved but the money hasn't appeared in my account.",
            "I need to return a defective product for a full refund.",
            "The refund form isn't working on your website.",
            "Can I get a partial refund for unused service?",
            "My refund request was denied without explanation.",
            "I need a refund because the product didn't match the description.",
        ],
    },
    "delivery": {
        "weight": 0.10,
        "messages": [
            "My package hasn't arrived yet and tracking shows it's delivered.",
            "Can I change the delivery address for my order?",
            "The estimated delivery date keeps changing.",
            "My order arrived damaged. Need a replacement.",
            "Tracking number provided doesn't work.",
            "I received the wrong items in my delivery.",
            "Can I schedule a specific delivery time slot?",
            "The delivery driver left my package in the rain.",
            "International shipping is taking longer than expected.",
            "I need to cancel my order before it ships.",
        ],
    },
    "subscriptions": {
        "weight": 0.12,
        "messages": [
            "How do I cancel my subscription?",
            "I want to upgrade from Free to Pro plan.",
            "My subscription auto-renewed and I wanted to cancel.",
            "Can I pause my subscription for a month?",
            "The features listed for my plan aren't available.",
            "I'm being charged for a plan I didn't sign up for.",
            "How do I add more team members to my subscription?",
            "Annual vs monthly pricing — which is better?",
            "My subscription benefits disappeared after an update.",
            "Can I switch from annual to monthly billing?",
            "Student discount not being applied to my subscription.",
            "I need an enterprise quote for 50+ users.",
        ],
    },
    "mobile_app": {
        "weight": 0.12,
        "messages": [
            "The app is very slow on my iPhone.",
            "Push notifications aren't working on Android.",
            "The app crashes when I try to view my orders.",
            "Camera feature in the app isn't working.",
            "App drains my battery very quickly.",
            "The mobile app layout is broken on my tablet.",
            "Offline mode doesn't seem to work properly.",
            "App doesn't sync with the web version.",
            "Dark mode is not available on the mobile app.",
            "The app size is too large, takes too much storage.",
            "Biometric login stopped working after the update.",
            "Can't download attachments in the mobile app.",
        ],
    },
    "technical_bugs": {
        "weight": 0.15,
        "messages": [
            "The dashboard keeps showing an error 500.",
            "Data export feature is producing empty CSV files.",
            "Search function returns no results even for exact matches.",
            "The notification bell shows wrong count of unread items.",
            "Images aren't loading on product pages.",
            "The analytics chart displays incorrect data.",
            "Copy-paste doesn't work in the text editor.",
            "Drag and drop feature broken in the latest update.",
            "API returns 403 error for authenticated requests.",
            "The date picker shows wrong timezone.",
            "File upload fails for any file larger than 5MB.",
            "Auto-save feature isn't working, lost my changes.",
            "The print feature cuts off content on the right side.",
            "Keyboard shortcuts stopped working.",
            "Browser console shows multiple JavaScript errors.",
        ],
    },
}

CHANNELS = ["email", "chat", "web_form", "mobile_app", "phone"]
CHANNEL_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10]

COUNTRIES = ["US", "GB", "DE", "FR", "CA", "AU", "IN", "BR", "NL", "RO", "ES", "IT", "JP"]
COUNTRY_WEIGHTS = [0.30, 0.12, 0.10, 0.08, 0.07, 0.05, 0.06, 0.04, 0.03, 0.05, 0.04, 0.03, 0.03]

PLATFORMS = ["Web-Chrome", "Web-Firefox", "Web-Safari", "iOS", "Android", "Web-Edge"]
PLATFORM_WEIGHTS = [0.30, 0.12, 0.10, 0.22, 0.20, 0.06]

PLANS = ["Free", "Pro", "Enterprise"]
PLAN_WEIGHTS = [0.40, 0.40, 0.20]

PRIORITIES = ["low", "medium", "high", "urgent"]
PRIORITY_WEIGHTS = [0.25, 0.40, 0.25, 0.10]

AGENTS = [
    "Sarah Johnson", "Mike Chen", "Ana Rodriguez", "James Wilson",
    "Priya Patel", "Tom Baker", "Maria Garcia", "David Kim",
    "Emily Taylor", "Carlos Santos", "Lisa Wang", "Ahmed Hassan",
]


def circadian_factor(hour: int, day_of_week: int) -> float:
    """
    Returns a volume multiplier based on time of day and day of week.
    Simulates realistic support traffic patterns.
    """
    # Weekend reduction (30-50% less)
    weekend_factor = 0.5 if day_of_week >= 5 else 1.0

    # Circadian pattern: peak at 10-11 AM and 2-3 PM, low at night
    hour_factors = {
        0: 0.05, 1: 0.03, 2: 0.02, 3: 0.02, 4: 0.03, 5: 0.05,
        6: 0.10, 7: 0.20, 8: 0.50, 9: 0.80, 10: 1.00, 11: 0.95,
        12: 0.70, 13: 0.85, 14: 1.00, 15: 0.90, 16: 0.75, 17: 0.55,
        18: 0.35, 19: 0.25, 20: 0.15, 21: 0.10, 22: 0.08, 23: 0.06,
    }

    return hour_factors.get(hour, 0.1) * weekend_factor


def generate_ticket(category: str, timestamp: datetime) -> dict:
    """Generate a single realistic ticket."""
    cat_data = CATEGORIES[category]
    message = random.choice(cat_data["messages"])

    # Add some variation to messages
    prefixes = ["", "Hi, ", "Hello, ", "Hey, ", "Hi team, ", "Dear support, "]
    suffixes = [
        "", " Thanks.", " Please help.", " This is urgent.",
        " Looking forward to hearing from you.", " Any help appreciated.",
    ]
    message = random.choice(prefixes) + message + random.choice(suffixes)

    return {
        "ticket_id": f"TK-{timestamp.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
        "customer_id": f"CUST-{random.randint(1000, 9999)}",
        "created_at": timestamp,
        "message": message.strip(),
        "category": category,
        "priority": random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS, k=1)[0],
        "status": random.choice(["open", "open", "open", "in_progress", "resolved"]),
        "assigned_agent": random.choice(AGENTS),
        "channel": random.choices(CHANNELS, weights=CHANNEL_WEIGHTS, k=1)[0],
        "country": random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0],
        "product": "CloudFlow Analytics",
        "platform_device": random.choices(PLATFORMS, weights=PLATFORM_WEIGHTS, k=1)[0],
        "customer_plan": random.choices(PLANS, weights=PLAN_WEIGHTS, k=1)[0],
    }


def main():
    """Generate and insert historical ticket data."""
    print("=" * 70)
    print("AI Support Platform — Synthetic Historical Data Generator")
    print(f"   Company: CloudFlow Analytics")
    print(f"   Period: {DAYS_OF_HISTORY} days of history")
    print(f"   Target: ~{DAYS_OF_HISTORY * TICKETS_PER_DAY_AVG} tickets")
    print("=" * 70)

    # Create tables
    with sync_engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "vector"'))
    Base.metadata.create_all(sync_engine)
    print("Database tables created")

    # Generate tickets
    now = datetime.now(timezone.utc)
    all_tickets = []
    hourly_counts = defaultdict(lambda: defaultdict(int))
    hourly_sentiments = defaultdict(lambda: defaultdict(list))

    category_names = list(CATEGORIES.keys())
    category_weights = [CATEGORIES[c]["weight"] for c in category_names]

    print("\nGenerating tickets...")

    for day_offset in range(DAYS_OF_HISTORY, 0, -1):
        day_date = now - timedelta(days=day_offset)
        day_of_week = day_date.weekday()

        # Vary daily volume slightly
        daily_volume = int(TICKETS_PER_DAY_AVG * random.uniform(0.8, 1.2))

        for _ in range(daily_volume):
            # Pick hour based on circadian pattern
            hours = list(range(24))
            hour_weights = [circadian_factor(h, day_of_week) for h in hours]
            hour = random.choices(hours, weights=hour_weights, k=1)[0]

            timestamp = day_date.replace(
                hour=hour,
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
                microsecond=0,
            )

            # Pick category
            category = random.choices(category_names, weights=category_weights, k=1)[0]

            ticket = generate_ticket(category, timestamp)
            all_tickets.append(ticket)

            # Track hourly stats for baseline
            hourly_counts[category][(day_of_week, hour)] += 1

        if day_offset % 5 == 0:
            print(f"   Day -{day_offset}: {daily_volume} tickets generated")

    # Sort by timestamp
    all_tickets.sort(key=lambda t: t["created_at"])
    total = len(all_tickets)
    print(f"\nGenerated {total} tickets total")

    # Compute embeddings in batches
    print("\nComputing embeddings (this may take a few minutes)...")
    messages = [t["message"] for t in all_tickets]
    BATCH_SIZE = 256

    all_embeddings = []
    for i in range(0, len(messages), BATCH_SIZE):
        batch = messages[i:i + BATCH_SIZE]
        embeddings = embedding_service.embed_batch(batch)
        all_embeddings.extend(embeddings)
        pct = min(100, round((i + BATCH_SIZE) / len(messages) * 100))
        print(f"   Embedded: {min(i + BATCH_SIZE, len(messages))}/{len(messages)} ({pct}%)")

    # Compute sentiments
    print("\nComputing sentiment scores...")
    sentiments = [compute_sentiment(msg) for msg in messages]

    # Insert into database
    print("\nInserting into database...")
    session = SyncSessionLocal()

    try:
        INSERT_BATCH = 500
        for i in range(0, total, INSERT_BATCH):
            batch_end = min(i + INSERT_BATCH, total)
            for j in range(i, batch_end):
                t = all_tickets[j]
                ticket = Ticket(
                    ticket_id=t["ticket_id"],
                    customer_id=t["customer_id"],
                    created_at=t["created_at"],
                    message=t["message"],
                    category=t["category"],
                    priority=t["priority"],
                    status=t["status"],
                    assigned_agent=t["assigned_agent"],
                    channel=t["channel"],
                    country=t["country"],
                    product=t["product"],
                    platform_device=t["platform_device"],
                    customer_plan=t["customer_plan"],
                    sentiment_score=sentiments[j],
                    embedding=all_embeddings[j],
                )
                session.add(ticket)

                # Track for baseline
                cat = t["category"]
                dow = t["created_at"].weekday()
                h = t["created_at"].hour
                hourly_sentiments[cat][(dow, h)].append(sentiments[j])

            session.commit()
            pct = round(batch_end / total * 100)
            print(f"   Inserted: {batch_end}/{total} ({pct}%)")

        # Compute and insert baseline metrics
        print("\nComputing baseline metrics...")
        for category in CATEGORIES:
            for dow in range(7):
                for hour in range(24):
                    key = (dow, hour)
                    count = hourly_counts[category].get(key, 0)
                    sent_list = hourly_sentiments[category].get(key, [])

                    # Normalize to per-day average (we have DAYS_OF_HISTORY days of data)
                    # But each day-of-week appears ~4 times in 30 days
                    days_with_this_dow = DAYS_OF_HISTORY // 7
                    avg_volume = count / max(days_with_this_dow, 1)
                    std_volume = max(avg_volume * 0.3, 1.0)  # Estimated std dev
                    avg_sent = sum(sent_list) / len(sent_list) if sent_list else -0.1

                    baseline = BaselineMetric(
                        category=category,
                        day_of_week=dow,
                        hour_of_day=hour,
                        avg_hourly_volume=round(avg_volume, 2),
                        std_hourly_volume=round(std_volume, 2),
                        avg_sentiment=round(avg_sent, 4),
                    )
                    session.add(baseline)

        session.commit()
        print("Baseline metrics computed and stored")

        print("\n" + "=" * 70)
        print("SEED COMPLETE")
        print(f"   Total tickets: {total}")
        print(f"   Baseline metrics: {len(CATEGORIES) * 7 * 24} entries")
        print(f"   Categories: {', '.join(CATEGORIES.keys())}")
        print("=" * 70)

    except Exception as e:
        session.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
