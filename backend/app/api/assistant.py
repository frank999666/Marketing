from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.schemas.chat import ChatMessage, ChatResponse
from app.api.auth import get_current_company
from app.services.ai_content import AIContentService

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    ai_service = AIContentService()

    # Gather context about the company
    context = {
        "company_name": company.name,
        "brand_config": company.brand_config,
    }

    # Add brand profile if exists
    if company.brand_profile:
        context["brand_profile"] = {
            "industry": company.brand_profile.industry,
            "tone": company.brand_profile.tone,
            "target_audience": company.brand_profile.target_audience,
        }

    # Add analytics summary if available
    from app.models.social import SocialAccount, AnalyticsSnapshot
    accounts = db.query(SocialAccount).filter(SocialAccount.company_id == company.id).all()
    if accounts:
        context["social_accounts"] = [
            {
                "platform": a.platform,
                "username": a.username,
                "followers": a.profile_data.get("followers", 0),
            }
            for a in accounts
        ]

    # Add recent posts
    from app.models.content import Post
    recent_posts = (
        db.query(Post)
        .filter(Post.company_id == company.id)
        .order_by(Post.created_at.desc())
        .limit(10)
        .all()
    )
    if recent_posts:
        context["recent_posts"] = [
            {
                "platform": p.platform,
                "title": p.title,
                "status": p.status,
                "metrics": p.metrics,
            }
            for p in recent_posts
        ]

    response = await ai_service.chat_assistant(
        message=message.message,
        company_context=context,
        extra_context=message.context,
    )

    return ChatResponse(
        response=response["answer"],
        sources=response.get("sources", []),
        suggestions=response.get("suggestions", []),
    )
