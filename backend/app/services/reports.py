from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.company import Company
from app.models.social import SocialAccount, AnalyticsSnapshot
from app.models.content import Post


class ReportService:

    def generate(
        self,
        company: Company,
        report_type: str,
        period_start: date,
        period_end: date,
        db: Session,
    ) -> dict:
        accounts = db.query(SocialAccount).filter(SocialAccount.company_id == company.id).all()
        account_ids = [a.id for a in accounts]

        # Get posts in period
        posts = (
            db.query(Post)
            .filter(
                Post.company_id == company.id,
                Post.created_at >= period_start,
                Post.created_at <= period_end,
            )
            .all()
        )

        # Get analytics
        metrics = {}
        if account_ids:
            snapshots = (
                db.query(
                    AnalyticsSnapshot.metric_type,
                    func.sum(AnalyticsSnapshot.metric_value),
                )
                .filter(
                    AnalyticsSnapshot.social_account_id.in_(account_ids),
                    AnalyticsSnapshot.snapshot_date >= period_start,
                    AnalyticsSnapshot.snapshot_date <= period_end,
                )
                .group_by(AnalyticsSnapshot.metric_type)
                .all()
            )
            metrics = {m[0]: m[1] for m in snapshots}

        # Platform breakdown
        platform_stats = {}
        for account in accounts:
            platform_stats[account.platform] = {
                "username": account.username,
                "followers": account.profile_data.get("followers", 0),
            }

        # Post performance
        published_posts = [p for p in posts if p.status == "published"]

        total_reach = metrics.get("reach", 0)
        total_engagement = metrics.get("engagement", 0)
        engagement_rate = (total_engagement / total_reach * 100) if total_reach > 0 else 0

        report = {
            "summary": {
                "period": f"{period_start} to {period_end}",
                "report_type": report_type,
                "total_posts": len(posts),
                "published_posts": len(published_posts),
                "total_followers": sum(
                    a.profile_data.get("followers", 0) for a in accounts
                ),
            },
            "metrics": {
                "total_reach": total_reach,
                "total_impressions": metrics.get("impressions", 0),
                "total_engagement": total_engagement,
                "engagement_rate": round(engagement_rate, 2),
                "followers_gained": metrics.get("followers_gained", 0),
            },
            "platform_breakdown": platform_stats,
            "top_posts": self._get_top_posts(posts),
            "recommendations": self._generate_recommendations(metrics, posts, accounts),
        }

        return report

    def _get_top_posts(self, posts: list) -> list:
        published = [p for p in posts if p.status == "published" and p.metrics]
        sorted_posts = sorted(
            published,
            key=lambda p: p.metrics.get("engagement", 0),
            reverse=True,
        )
        return [
            {
                "platform": p.platform,
                "title": p.title,
                "engagement": p.metrics.get("engagement", 0),
                "reach": p.metrics.get("reach", 0),
            }
            for p in sorted_posts[:5]
        ]

    def _generate_recommendations(self, metrics: dict, posts: list, accounts: list) -> list:
        recommendations = []

        if metrics.get("engagement", 0) < 100:
            recommendations.append(
                "El engagement es bajo. Considera crear contenido más interactivo como encuestas o preguntas."
            )

        published = [p for p in posts if p.status == "published"]
        if len(published) < 4:
            recommendations.append(
                "Publicaste poco este período. Intenta mantener una frecuencia de al menos 3 posts por semana."
            )

        if not accounts:
            recommendations.append(
                "Conecta tus redes sociales para obtener métricas automatizadas."
            )

        if not recommendations:
            recommendations.append("Sigue manteniendo el ritmo actual. Los números van bien.")

        return recommendations
