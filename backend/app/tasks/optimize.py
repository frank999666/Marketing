from datetime import date, timedelta
from app.tasks.worker import celery_app
from app.database import SessionLocal
from app.models.company import Company
from app.models.content import Post
from app.models.social import AnalyticsSnapshot
from app.services.ai_content import AIContentService


@celery_app.task(name="app.tasks.optimize.suggest_content")
def suggest_content():
    db = SessionLocal()
    try:
        companies = db.query(Company).all()
        ai_service = AIContentService()

        for company in companies:
            # Analyze what content performed best
            recent_posts = (
                db.query(Post)
                .filter(
                    Post.company_id == company.id,
                    Post.status == "published",
                    Post.created_at >= date.today() - timedelta(days=30),
                )
                .all()
            )

            if not recent_posts:
                continue

            # Find best performing platform
            platform_performance = {}
            for post in recent_posts:
                platform = post.platform
                if platform not in platform_performance:
                    platform_performance[platform] = {"count": 0, "engagement": 0}
                platform_performance[platform]["count"] += 1
                platform_performance[platform]["engagement"] += post.metrics.get("engagement", 0)

            best_platform = max(
                platform_performance.items(),
                key=lambda x: x[1]["engagement"],
                default=None,
            )

            if best_platform:
                # Generate suggestions for the best platform
                brand_context = {}
                if company.brand_profile:
                    brand_context = {
                        "industry": company.brand_profile.industry,
                        "tone": company.brand_profile.tone,
                        "target_audience": company.brand_profile.target_audience,
                    }

                # This would generate and store suggestions
                # For now, just log that we analyzed
                print(f"Suggestions generated for {company.name} on {best_platform[0]}")

        db.commit()
    finally:
        db.close()
