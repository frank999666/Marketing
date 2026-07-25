from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.content import Post
from app.schemas.content import PostCreate, PostResponse, ContentGenerateRequest, ContentGenerateResponse
from app.api.auth import get_current_user, get_current_company
from app.services.ai_content import AIContentService

router = APIRouter(prefix="/content", tags=["content"])


@router.get("", response_model=List[PostResponse])
def list_posts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    query = db.query(Post).filter(Post.company_id == company.id)
    if platform:
        query = query.filter(Post.platform == platform)
    if status:
        query = query.filter(Post.status == status)
    return query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=PostResponse)
def create_post(
    post_data: PostCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    post = Post(
        company_id=company.id,
        platform=post_data.platform,
        content_type=post_data.content_type,
        title=post_data.title,
        body=post_data.body,
        hashtags=post_data.hashtags,
        cta=post_data.cta,
        image_url=post_data.image_url,
        scheduled_at=post_data.scheduled_at,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.company_id == company.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: UUID,
    post_data: PostCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.company_id == company.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    for field, value in post_data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}")
def delete_post(
    post_id: UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.company_id == company.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"detail": "Post deleted"}


@router.post("/generate", response_model=ContentGenerateResponse)
async def generate_content(
    request: ContentGenerateRequest,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    ai_service = AIContentService()

    # Get brand profile for context
    brand_profile = company.brand_profile
    brand_context = {}
    if brand_profile:
        brand_context = {
            "industry": brand_profile.industry,
            "tone": brand_profile.tone,
            "values": brand_profile.values,
            "target_audience": brand_profile.target_audience,
        }

    variations = await ai_service.generate_content(
        platform=request.platform,
        content_type=request.content_type,
        topic=request.topic,
        brand_context=brand_context,
        num_variations=request.num_variations,
    )

    image_url = None
    if request.include_image:
        image_url = await ai_service.generate_image(
            prompt=request.image_prompt or request.topic or "Marketing image",
            platform=request.platform,
        )

    return ContentGenerateResponse(
        variations=variations,
        image_url=image_url,
    )
