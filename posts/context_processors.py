from django.db.models import Sum
from .models import Donation

LEVELS = [
    (0, "visitor", "Visitor"),
    (10, "new", "New Supporter"),
    (49, "friend", "Friend"),
    (100, "supporter", "Supporter"),
    (250, "advanced", "Advanced Supporter"),
    (500, "elite", "Elite Supporter"),
    (1000, "legend", "Legend"),
    (1500, "whale", "VIP Whale"),
]


def donation_context(request):
    if not request.user.is_authenticated:
        return {
            "donation_total": 0,
            "donation_level": "visitor",
            "donation_level_name": "Visitor",
            "donation_progress": 0,
            "next_goal": 10,
            "next_level": "new",
        }

    total = Donation.objects.filter(user=request.user).aggregate(
        total=Sum("amount")
    )["total"] or 0

    total += getattr(request.user.profile, "bonus_donations", 0)

    level = "visitor"
    level_name = "Visitor"

    next_level = None
    next_target = None
    next_goal = 0

    for i, (threshold, lvl, name) in enumerate(LEVELS):
        if total >= threshold:
            level = lvl
            level_name = name

            if i + 1 < len(LEVELS):
                next_target, next_level, _ = LEVELS[i + 1]
                next_goal = max(next_target - total, 0)
            else:
                next_target = None
                next_level = None
                next_goal = 0

    if next_target:
        donation_progress = min((total / next_target) * 100, 100)
    else:
        donation_progress = 100

    return {
        "donation_total": total,
        "donation_level": level,
        "donation_level_name": level_name,
        "donation_progress": donation_progress,
        "next_goal": next_goal,
        "next_level": next_level,
    }