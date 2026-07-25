from typing import List, Optional
from uuid import UUID
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.company import Company
from app.models.social import SocialAccount, AnalyticsSnapshot, AnalyticsAlert
from app.schemas.analytics import AnalyticsOverview, AlertResponse
from app.api.auth import get_current_company

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_overview(
    days: int = Query(30, ge=1, le=365),
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    accounts = db.query(SocialAccount).filter(SocialAccount.company_id == company.id).all()

    total_followers = 0
    total_reach = 0
    total_impressions = 0
    total_engagement = 0
    platform_data = []

    for account in accounts:
        # Get latest follower count
        latest = (
            db.query(AnalyticsSnapshot)
            .filter(
                AnalyticsSnapshot.social_account_id == account.id,
                AnalyticsSnapshot.metric_type == "followers",
            )
            .order_by(AnalyticsSnapshot.snapshot_date.desc())
            .first()
        )

        followers = latest.metric_value if latest else account.profile_data.get("followers", 0)

        # Get metrics for the period
        start_date = date.today() - timedelta(days=days)
        metrics = (
            db.query(AnalyticsSnapshot.metric_type, func.sum(AnalyticsSnapshot.metric_value))
            .filter(
                AnalyticsSnapshot.social_account_id == account.id,
                AnalyticsSnapshot.snapshot_date >= start_date,
            )
            .group_by(AnalyticsSnapshot.metric_type)
            .all()
        )

        metrics_dict = {m[0]: m[1] for m in metrics}

        total_followers += followers
        total_reach += metrics_dict.get("reach", 0)
        total_impressions += metrics_dict.get("impressions", 0)
        total_engagement += metrics_dict.get("engagement", 0)

        platform_data.append({
            "platform": account.platform,
            "username": account.username,
            "followers": followers,
            "reach": metrics_dict.get("reach", 0),
            "engagement": metrics_dict.get("engagement", 0),
        })

    engagement_rate = (total_engagement / total_reach * 100) if total_reach > 0 else 0

    return AnalyticsOverview(
        total_followers=total_followers,
        total_reach=total_reach,
        total_impressions=total_impressions,
        total_engagement=total_engagement,
        engagement_rate=round(engagement_rate, 2),
        platforms=platform_data,
    )


@router.get("/trends")
def get_trends(
    metric: str = Query("followers", regex="^(followers|reach|engagement|impressions)$"),
    days: int = Query(30, ge=1, le=365),
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    accounts = db.query(SocialAccount).filter(SocialAccount.company_id == company.id).all()
    account_ids = [a.id for a in accounts]

    start_date = date.today() - timedelta(days=days)

    snapshots = (
        db.query(AnalyticsSnapshot)
        .filter(
            AnalyticsSnapshot.social_account_id.in_(account_ids),
            AnalyticsSnapshot.metric_type == metric,
            AnalyticsSnapshot.snapshot_date >= start_date,
        )
        .order_by(AnalyticsSnapshot.snapshot_date)
        .all()
    )

    # Group by date
    trends = {}
    for snap in snapshots:
        date_str = str(snap.snapshot_date)
        if date_str not in trends:
            trends[date_str] = 0
        trends[date_str] += snap.metric_value

    return [{"date": d, "value": v, "metric": metric} for d, v in sorted(trends.items())]


@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    acknowledged: Optional[bool] = None,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    query = db.query(AnalyticsAlert).filter(AnalyticsAlert.company_id == company.id)
    if acknowledged is not None:
        query = query.filter(AnalyticsAlert.acknowledged == acknowledged)
    return query.order_by(AnalyticsAlert.created_at.desc()).limit(50).all()


@router.put("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    alert = db.query(AnalyticsAlert).filter(
        AnalyticsAlert.id == alert_id,
        AnalyticsAlert.company_id == company.id,
    ).first()
    if not alert:
        return {"error": "Alert not found"}
    alert.acknowledged = True
    db.commit()
    return {"detail": "Alert acknowledged"}
