from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from budget.models import Budget, Expense

MONEY_QUANT = Decimal("0.01")
ZERO = Decimal("0.00")


def _to_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _safe_div(numerator: Decimal, denominator: int) -> Decimal:
    if denominator <= 0:
        return ZERO
    return _to_money(numerator / Decimal(denominator))


def _month_bounds(as_of: date) -> tuple[date, date]:
    month_start = as_of.replace(day=1)
    _, days_in_month = calendar.monthrange(as_of.year, as_of.month)
    month_end = month_start + timedelta(days=days_in_month - 1)
    return month_start, month_end


def _velocity_status(spent_per_day: Decimal, target_daily_limit: Decimal) -> str:
    if target_daily_limit == ZERO:
        return "on_pace" if spent_per_day == ZERO else "behind"

    tolerance = abs(target_daily_limit) * Decimal("0.05")
    diff = spent_per_day - target_daily_limit
    if abs(diff) <= tolerance:
        return "on_pace"
    if diff < ZERO:
        return "ahead"
    return "behind"


def get_dashboard_metrics(user, as_of: date | None = None) -> dict:
    if as_of is None:
        as_of = timezone.localdate()

    month_start, month_end = _month_bounds(as_of)
    _, days_in_month = calendar.monthrange(as_of.year, as_of.month)
    elapsed_days = max(as_of.day, 1)
    remaining_days = max(days_in_month - as_of.day + 1, 1)

    total_budget = Budget.objects.filter(
        user=user,
        month=month_start,
        is_deleted=False,
    ).aggregate(total=Coalesce(Sum("amount"), ZERO))["total"]

    total_spent = Expense.objects.filter(
        user=user,
        date__gte=month_start,
        date__lte=month_end,
        is_deleted=False,
    ).aggregate(total=Coalesce(Sum("amount"), ZERO))["total"]

    total_budget = _to_money(total_budget)
    total_spent = _to_money(total_spent)

    remaining_budget = _to_money(total_budget - total_spent)
    daily_limit = _safe_div(remaining_budget, remaining_days)
    spent_per_day = _safe_div(total_spent, elapsed_days)

    has_budget = total_budget > ZERO
    has_expenses = total_spent > ZERO

    if not has_budget:
        empty_state = "no_budget"
        velocity_status = "no_budget"
        on_track = False
    elif not has_expenses:
        empty_state = "no_expenses"
        velocity_status = "ahead"
        on_track = True
    else:
        empty_state = None
        velocity_status = _velocity_status(spent_per_day, daily_limit)
        on_track = spent_per_day <= daily_limit

    return {
        "month_start": month_start,
        "month_end": month_end,
        "days_in_month": days_in_month,
        "elapsed_days": elapsed_days,
        "remaining_days": remaining_days,
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget,
        "daily_limit": daily_limit,
        "spent_per_day": spent_per_day,
        "on_track": on_track,
        "velocity_status": velocity_status,
        "has_budget": has_budget,
        "has_expenses": has_expenses,
        "empty_state": empty_state,
    }
