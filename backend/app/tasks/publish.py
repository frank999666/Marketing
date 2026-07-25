from datetime import datetime
from app.tasks.worker import celery_app
from app.database import SessionLocal
from app.models.content import Post
from app.models.social import SocialAccount
from app.services.social_manager import SocialManagerService


@celery_app.task(name="app.tasks.publish.publish_scheduled")
def publish_scheduled():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        scheduled_posts = (
            db.query(Post)
            .filter(
                Post.status == "scheduled",
                Post.scheduled_at <= now,
            )
            .all()
        )

        social_service = SocialManagerService()

        for post in scheduled_posts:
            try:
                account = db.query(SocialAccount).filter(
                    SocialAccount.company_id == post.company_id,
                    SocialAccount.platform == post.platform,
                ).first()

                if not account:
                    post.status = "failed"
                    continue

                result = social_service.publish.__wrapped__(
                    platform=post.platform,
                    account=account,
                    content={
                        "text": post.body,
                        "hashtags": post.hashtags,
                        "image_url": post.image_url,
                        "cta": post.cta,
                    },
                )

                post.status = "published"
                post.published_at = now
                post.post_id_external = result.get("post_id")

            except Exception as e:
                post.status = "failed"
                post.metrics = {"error": str(e)}

        db.commit()
    finally:
        db.close()
