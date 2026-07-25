from datetime import datetime, date
from app.tasks.worker import celery_app
from app.database import SessionLocal
from app.models.social import SocialAccount, AnalyticsSnapshot, AnalyticsAlert
from app.models.company import Company
from app.services.social_manager import SocialManagerService


@celery_app.task(name="app.tasks.monitor.sync_metrics")
def sync_metrics():
    db = SessionLocal()
    try:
        accounts = db.query(SocialAccount).all()
        social_service = SocialManagerService()

        for account in accounts:
            try:
                metrics = social_service.fetch_metrics.__wrapped__(
                    platform=account.platform,
                    account=account,
                )

                if metrics.get("followers"):
                    snapshot = AnalyticsSnapshot(
                        social_account_id=account.id,
                        metric_type="followers",
                        metric_value=metrics["followers"],
                        snapshot_date=date.today(),
                    )
                    db.add(snapshot)

                account.last_synced = datetime.utcnow()
                account.profile_data.update(metrics)

            except Exception as e:
                print(f"Error syncing {account.platform}: {e}")

        db.commit()
    finally:
        db.close()


@celery_app.task(name="app.tasks.monitor.detect_anomalies")
def detect_anomalies():
    db = SessionLocal()
    try:
        companies = db.query(Company).all()

        for company in companies:
            accounts = db.query(SocialAccount).filter(
                SocialAccount.company_id == company.id
            ).all()

            for account in accounts:
                # Get last 7 days of metrics
                from datetime import timedelta
                week_ago = date.today() - timedelta(days=7)
                two_weeks_ago = date.today() - timedelta(days=14)

                current_week = (
                    db.query(AnalyticsSnapshot)
                    .filter(
                        AnalyticsSnapshot.social_account_id == account.id,
                        AnalyticsSnapshot.metric_type == "followers",
                        AnalyticsSnapshot.snapshot_date >= week_ago,
                    )
                    .order_by(AnalyticsSnapshot.snapshot_date.desc())
                    .first()
                )

                previous_week = (
                    db.query(AnalyticsSnapshot)
                    .filter(
                        AnalyticsSnapshot.social_account_id == account.id,
                        AnalyticsSnapshot.metric_type == "followers",
                        AnalyticsSnapshot.snapshot_date >= two_weeks_ago,
                        AnalyticsSnapshot.snapshot_date < week_ago,
                    )
                    .order_by(AnalyticsSnapshot.snapshot_date.desc())
                    .first()
                )

                if current_week and previous_week:
                    change = current_week.metric_value - previous_week.metric_value
                    if change < -50:  # Lost more than 50 followers
                        alert = AnalyticsAlert(
                            company_id=company.id,
                            alert_type="follower_loss",
                            severity="warning",
                            title="Pérdida significativa de seguidores",
                            message=f"Has perdido {abs(change)} seguidores en los últimos 7 días en {account.platform}.",
                            explanation="Esto puede deberse a contenido no relevante, baja frecuencia de publicación, o cambios en el algoritmo.",
                            evidence={
                                "platform": account.platform,
                                "current": current_week.metric_value,
                                "previous": previous_week.metric_value,
                                "change": change,
                            },
                            suggested_actions=[
                                "Revisar el contenido publicado en los últimos 7 días",
                                "Aumentar la frecuencia de publicación",
                                "Crear contenido más interactivo",
                                "Analizar qué contenido generaba más engagement",
                            ],
                        )
                        db.add(alert)

        db.commit()
    finally:
        db.close()
