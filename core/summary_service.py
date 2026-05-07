from db.activity_repo import get_daily_info, get_targets_for_date, get_all_logged_dates
from core.meal_service import get_meal_summary, get_daily_totals
from core.activity_service import get_activities

def get_full_day_summary(date):
    info = get_daily_info(date)
    meals = get_meal_summary(date)
    totals = get_daily_totals(date)
    targets = get_targets_for_date(date)
    activities = get_activities(date)

    return {
        "date": date,
        "info": dict(info) if info else None,
        "meals": meals,
        "totals": totals,
        "targets": dict(targets) if targets else None,
        "activities": [dict(a) for a in activities]
    }

def get_all_dates():
    return get_all_logged_dates()

def date_has_data(date):
    info = get_daily_info(date)
    return info is not None