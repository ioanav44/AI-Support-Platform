"""
Simulator Service — Generates realistic synthetic ticket streams for demo scenarios.

Each scenario produces semantically similar but varied ticket messages
that will cluster together and trigger anomaly detection.
"""
import asyncio
import logging
import random
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ticket import TicketCreate
from app.services.pipeline_service import process_ticket
from app.services.websocket_manager import manager as ws_manager
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# --- Scenario Definitions ---

SCENARIOS = {
    "visa_outage": {
        "category": "payments",
        "messages": [
            "My Visa card payment is failing at checkout.",
            "Visa payment keeps getting declined, tried 3 times already.",
            "Can't complete my purchase with Visa card. Error at payment step.",
            "Getting error when paying with Visa. MasterCard works fine though.",
            "Checkout rejects my Visa card every time I try.",
            "Payment failure with Visa at the final step of checkout.",
            "I tried two different Visa cards and neither works.",
            "Error 402 when attempting to pay with my Visa card.",
            "Visa transaction fails immediately after entering card details.",
            "Your payment system won't accept any Visa cards right now.",
            "Been trying to pay with Visa for 30 minutes. Nothing works.",
            "Visa card declined at checkout but my bank shows no issue.",
            "Unable to process Visa payment. Is your payment gateway down?",
            "Tried purchasing subscription with Visa but it just spins and fails.",
            "Visa checkout broken? I keep getting a generic error message.",
            "Payment with Visa does not go through, getting timeout error.",
            "My colleague also can't pay with Visa. Is this a known issue?",
            "Visa payment rejected with error code CARD_DECLINED.",
            "Cannot finalize order with Visa. Getting 'transaction failed' error.",
            "Every Visa payment attempt results in an error. MasterCard still works.",
            "Visa card payment returns 'unable to process' message.",
            "Just got declined again trying Visa checkout. This is frustrating.",
            "Why is Visa not working on your platform?",
            "Payment error specifically with Visa cards at checkout page.",
            "Visa payment integration seems to be broken.",
        ],
        "countries": ["US", "US", "US", "GB", "DE", "CA", "FR", "US", "AU"],
        "platforms": ["Web-Chrome", "Web-Firefox", "iOS", "Android", "Web-Safari"],
        "plans": ["Pro", "Enterprise", "Pro", "Free", "Enterprise", "Pro"],
    },
    "login_bug": {
        "category": "login",
        "messages": [
            "I can't log into my account after the latest update.",
            "Login page shows a blank screen after entering my credentials.",
            "Getting 'invalid credentials' error even with correct password.",
            "Authentication fails every time since this morning.",
            "Can't sign in. The login button does nothing when I click it.",
            "Password reset email never arrives. Can't access my account.",
            "Two-factor authentication code is not being accepted.",
            "Login redirects me to a 404 page instead of my dashboard.",
            "SSO login is broken since the v4.2 release.",
            "My team of 15 people all got locked out at the same time.",
            "Login page crashes on mobile after the latest app update.",
            "Getting 'session expired' immediately after logging in.",
            "OAuth login with Google stopped working today.",
            "Unable to authenticate. Error says 'service unavailable'.",
            "Login works on web but not on the mobile app anymore.",
            "Account locked after a single failed login attempt. This is a bug.",
            "The sign-in process hangs at 'Verifying credentials...' forever.",
            "Can't access my account. Login just shows a spinning wheel.",
            "Authentication service seems down. Multiple team members affected.",
            "Login error: 'unexpected server response' after entering password.",
        ],
        "countries": ["US", "GB", "DE", "US", "CA", "FR", "IN", "US", "BR"],
        "platforms": ["Web-Chrome", "iOS", "Android", "Web-Firefox", "iOS", "Web-Chrome"],
        "plans": ["Enterprise", "Pro", "Pro", "Free", "Enterprise", "Pro"],
    },
    "delivery_delay": {
        "category": "delivery",
        "messages": [
            "My order hasn't arrived and it's been 2 weeks.",
            "Package tracking shows 'in transit' for 10 days now.",
            "Delivery estimated for last Monday but still not here.",
            "Where is my order? Tracking hasn't updated in a week.",
            "I ordered express shipping but package is extremely delayed.",
            "My shipment seems to be stuck at a distribution center.",
            "Order placed 3 weeks ago, no delivery date in sight.",
            "Tracking shows package arrived at customs 8 days ago.",
            "Multiple orders delayed. Is there a shipping issue?",
            "Expected delivery was 5 days ago. No updates since.",
            "My package has been 'out for delivery' for 3 days.",
            "Delivery delay is unacceptable. I needed this for an event.",
            "The courier hasn't picked up my package for over a week.",
            "Is there a warehouse issue? Everything seems delayed.",
            "I paid for 2-day shipping and it's been 9 days.",
        ],
        "countries": ["DE", "FR", "DE", "AT", "FR", "NL", "DE", "BE", "FR"],
        "platforms": ["Web-Chrome", "iOS", "Android", "Web-Firefox", "Web-Chrome"],
        "plans": ["Pro", "Free", "Enterprise", "Pro", "Free", "Pro"],
    },
    "mobile_crash": {
        "category": "mobile_app",
        "messages": [
            "App crashes immediately after opening on Android 14.",
            "The mobile app keeps force-closing after the latest update.",
            "App won't even load. Crashes on the splash screen.",
            "Getting repeated crashes on my Pixel 8 with the new version.",
            "App freezes and then crashes after about 5 seconds.",
            "Samsung Galaxy S24 - app crashes on launch every time.",
            "Updated the app today and now it won't stop crashing.",
            "Mobile app is completely unusable. Crashes on every action.",
            "The app closes itself randomly while browsing products.",
            "Can't use the app on my phone anymore. Instant crash.",
            "App crashes when trying to open settings or profile.",
            "Since version 5.2.0, the app crashes on my Android phone.",
            "Force close error on launch. Android 14, OnePlus 12.",
            "App was working fine yesterday. Today it won't open.",
            "Multiple crash reports from my team. All on Android 14.",
        ],
        "countries": ["US", "IN", "DE", "BR", "US", "GB", "FR", "JP", "US"],
        "platforms": ["Android", "Android", "Android", "Android", "Android", "Android"],
        "plans": ["Free", "Pro", "Enterprise", "Free", "Pro", "Free"],
    },
    "subscription_issue": {
        "category": "subscriptions",
        "messages": [
            "I was charged twice for my monthly subscription.",
            "My subscription was canceled without my consent.",
            "Cannot upgrade my plan from Free to Pro. Button does nothing.",
            "Subscription renewal failed but I have funds available.",
            "I downgraded my plan but I'm still being charged the old price.",
            "Free trial ended but I was charged without any warning.",
            "Subscription page shows wrong plan. I'm on Enterprise, shows Free.",
            "I canceled my subscription last month but was charged again.",
            "Can't see the subscription management page. Gets 500 error.",
            "My team was downgraded from Enterprise to Pro without notice.",
            "Annual subscription refund requested. Service not as promised.",
            "Billing shows two active subscriptions but I only have one.",
            "Subscription auto-renewed after I specifically turned it off.",
            "Promo code for subscription discount is not being applied.",
            "Can't cancel subscription. The cancel button is unresponsive.",
        ],
        "countries": ["US", "US", "GB", "CA", "DE", "US", "FR", "AU", "US"],
        "platforms": ["Web-Chrome", "iOS", "Android", "Web-Firefox", "Web-Chrome"],
        "plans": ["Pro", "Enterprise", "Free", "Pro", "Enterprise", "Pro"],
    },
}

AGENTS = [
    "Sarah Johnson", "Mike Chen", "Ana Rodriguez", "James Wilson",
    "Priya Patel", "Tom Baker", "Maria Garcia", "David Kim",
    "Emily Taylor", "Carlos Santos",
]


class SimulationRunner:
    """Manages running simulation scenarios."""

    def __init__(self):
        self._running: dict[str, bool] = {}
        self._stats: dict[str, dict] = {}

    @property
    def is_running(self) -> bool:
        return any(self._running.values())

    def get_status(self, scenario: str) -> dict:
        return self._stats.get(scenario, {"status": "IDLE", "tickets_injected": 0})

    async def run_scenario(self, scenario: str, speed: int = 5, ticket_count: int = 150):
        """Run a simulation scenario asynchronously."""
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}")

        if self._running.get(scenario):
            logger.warning(f"Scenario {scenario} already running")
            return

        self._running[scenario] = True
        self._stats[scenario] = {
            "status": "RUNNING",
            "tickets_injected": 0,
            "total_planned": ticket_count,
            "elapsed_seconds": 0,
        }

        try:
            await self._inject_tickets(scenario, speed, ticket_count)
        finally:
            self._running[scenario] = False
            self._stats[scenario]["status"] = "COMPLETED"

    async def _inject_tickets(self, scenario: str, speed: int, total: int):
        """Inject tickets at the specified speed."""
        config = SCENARIOS[scenario]
        messages = config["messages"]
        start_time = datetime.now(timezone.utc)
        delay = 1.0 / speed  # seconds between tickets

        for i in range(total):
            if not self._running.get(scenario):
                break

            # Generate realistic ticket data
            now = datetime.now(timezone.utc)
            ticket_data = TicketCreate(
                ticket_id=f"TK-SIM-{uuid.uuid4().hex[:8].upper()}",
                customer_id=f"CUST-{random.randint(1000, 9999)}",
                created_at=now,
                message=random.choice(messages),
                category=config["category"],
                priority=random.choice(["high", "urgent", "high", "medium"]),
                status="open",
                assigned_agent=random.choice(AGENTS),
                channel=random.choice(["email", "chat", "web_form", "mobile_app"]),
                country=random.choice(config["countries"]),
                product="CloudFlow Analytics",
                platform_device=random.choice(config["platforms"]),
                customer_plan=random.choice(config["plans"]),
            )

            # Process through the full pipeline
            async with AsyncSessionLocal() as db:
                try:
                    await process_ticket(db, ticket_data)
                    await db.commit()
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Simulation ticket error: {e}")

            self._stats[scenario]["tickets_injected"] = i + 1
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._stats[scenario]["elapsed_seconds"] = round(elapsed, 1)

            # Broadcast progress
            await ws_manager.broadcast({
                "event": "SIMULATION_PROGRESS",
                "data": {
                    "scenario": scenario,
                    "injected": i + 1,
                    "total": total,
                    "rate": f"{speed} tix/s",
                }
            })

            await asyncio.sleep(delay)

        logger.info(f"Simulation '{scenario}' completed: {self._stats[scenario]['tickets_injected']} tickets injected.")

    def stop_scenario(self, scenario: str):
        """Stop a running scenario."""
        self._running[scenario] = False


simulator = SimulationRunner()
