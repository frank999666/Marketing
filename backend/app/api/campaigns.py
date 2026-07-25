from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.campaign import AdCampaign, AdCreative
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignGenerateRequest
from app.api.auth import get_current_user, get_current_company
from app.services.ai_content import AIContentService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=List[CampaignResponse])
def list_campaigns(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    return db.query(AdCampaign).filter(AdCampaign.company_id == company.id).order_by(AdCampaign.created_at.desc()).all()


@router.post("", response_model=CampaignResponse)
def create_campaign(
    campaign_data: CampaignCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    campaign = AdCampaign(
        company_id=company.id,
        **campaign_data.model_dump(),
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    campaign = db.query(AdCampaign).filter(
        AdCampaign.id == campaign_id,
        AdCampaign.company_id == company.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: UUID,
    campaign_data: CampaignCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    campaign = db.query(AdCampaign).filter(
        AdCampaign.id == campaign_id,
        AdCampaign.company_id == company.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    for field, value in campaign_data.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)

    db.commit()
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/approve")
def approve_campaign(
    campaign_id: UUID,
    user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    campaign = db.query(AdCampaign).filter(
        AdCampaign.id == campaign_id,
        AdCampaign.company_id == company.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.approved = True
    campaign.approved_by = user.id
    campaign.status = "active"
    db.commit()

    return {"detail": "Campaign approved and activated"}


@router.post("/generate")
async def generate_campaign(
    request: CampaignGenerateRequest,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    brand_profile = company.brand_profile
    brand_context = {}
    if brand_profile:
        brand_context = {
            "industry": brand_profile.industry,
            "tone": brand_profile.tone,
            "target_audience": brand_profile.target_audience,
        }

    ai_service = AIContentService()
    result = await ai_service.generate_campaign_strategy(
        objective=request.objective,
        budget=float(request.budget),
        target_audience=request.target_audience,
        product_description=request.product_description,
        brand_context=brand_context,
    )

    # Create campaign
    campaign = AdCampaign(
        company_id=company.id,
        name=result["campaign_name"],
        platform=result["platform"],
        objective=request.objective,
        budget=request.budget,
        audience_config=result.get("audience_config", {}),
        status="draft",
    )
    db.add(campaign)
    db.flush()

    # Create creatives
    for creative_data in result.get("creatives", []):
        creative = AdCreative(
            campaign_id=campaign.id,
            copy=creative_data.get("copy"),
            headline=creative_data.get("headline"),
            description=creative_data.get("description"),
            cta=creative_data.get("cta"),
            variant=creative_data.get("variant", "A"),
        )
        db.add(creative)

    db.commit()
    db.refresh(campaign)

    return {
        "campaign": CampaignResponse.model_validate(campaign),
        "strategy_summary": result.get("strategy_summary", ""),
        "creatives": result.get("creatives", []),
    }
