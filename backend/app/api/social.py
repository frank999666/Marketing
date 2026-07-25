from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.models.social import SocialAccount, AnalyticsSnapshot
from app.models.content import Post
from app.schemas.social import SocialAccountResponse, ConnectRequest, PublishRequest
from app.api.auth import get_current_company
from app.services.social_manager import SocialManagerService

router = APIRouter(prefix="/social", tags=["social"])


@router.get("/accounts", response_model=List[SocialAccountResponse])
def list_accounts(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    return db.query(SocialAccount).filter(SocialAccount.company_id == company.id).all()


@router.post("/connect", response_model=SocialAccountResponse)
async def connect_account(
    connect_data: ConnectRequest,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    social_service = SocialManagerService()
    account_data = await social_service.exchange_token(
        platform=connect_data.platform,
        auth_code=connect_data.auth_code,
        redirect_uri=connect_data.redirect_uri,
    )

    account = SocialAccount(
        company_id=company.id,
        platform=connect_data.platform,
        account_id=account_data["account_id"],
        access_token=account_data["access_token"],
        refresh_token=account_data.get("refresh_token"),
        username=account_data.get("username"),
        profile_data=account_data.get("profile_data", {}),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.delete("/accounts/{account_id}")
def disconnect_account(
    account_id: UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    account = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.company_id == company.id,
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    db.commit()
    return {"detail": "Account disconnected"}


@router.post("/publish")
async def publish_post(
    publish_data: PublishRequest,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(
        Post.id == publish_data.post_id,
        Post.company_id == company.id,
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    social_service = SocialManagerService()
    results = []

    for platform in publish_data.platforms:
        account = db.query(SocialAccount).filter(
            SocialAccount.company_id == company.id,
            SocialAccount.platform == platform,
        ).first()

        if not account:
            results.append({"platform": platform, "status": "error", "message": "Account not connected"})
            continue

        try:
            result = await social_service.publish(
                platform=platform,
                account=account,
                content={
                    "text": post.body,
                    "hashtags": post.hashtags,
                    "image_url": post.image_url,
                    "cta": post.cta,
                },
            )
            results.append({"platform": platform, "status": "success", "post_id": result.get("post_id")})

            # Update post status
            if len(publish_data.platforms) == 1:
                post.status = "published"
                post.published_at = datetime.utcnow()
                post.post_id_external = result.get("post_id")

        except Exception as e:
            results.append({"platform": platform, "status": "error", "message": str(e)})

    db.commit()
    return {"results": results}


@router.get("/analytics/overview")
def get_analytics_overview(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    accounts = db.query(SocialAccount).filter(SocialAccount.company_id == company.id).all()

    overview = {
        "total_followers": 0,
        "platforms": [],
    }

    for account in accounts:
        latest_snapshot = (
            db.query(AnalyticsSnapshot)
            .filter(AnalyticsSnapshot.social_account_id == account.id)
            .order_by(AnalyticsSnapshot.snapshot_date.desc())
            .first()
        )

        platform_data = {
            "platform": account.platform,
            "username": account.username,
            "followers": account.profile_data.get("followers", 0),
        }

        if latest_snapshot:
            platform_data["last_synced"] = str(latest_snapshot.snapshot_date)

        overview["total_followers"] += platform_data["followers"]
        overview["platforms"].append(platform_data)

    return overview
