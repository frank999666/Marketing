import pytest
from pydantic import ValidationError


class TestUserCreate:
    def test_valid_user(self):
        from app.schemas.user import UserCreate
        user = UserCreate(email="test@example.com", password="Secure123", name="Test User")
        assert user.email == "test@example.com"
        assert user.name == "Test User"

    def test_password_too_short(self):
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError, match="at least 8 characters"):
            UserCreate(email="test@example.com", password="Ab1", name="Test")

    def test_password_no_uppercase(self):
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError, match="uppercase"):
            UserCreate(email="test@example.com", password="secure123", name="Test")

    def test_password_no_lowercase(self):
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError, match="lowercase"):
            UserCreate(email="test@example.com", password="SECURE123", name="Test")

    def test_password_no_digit(self):
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError, match="digit"):
            UserCreate(email="test@example.com", password="SecurePass", name="Test")

    def test_name_too_short(self):
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError, match="at least 2 characters"):
            UserCreate(email="test@example.com", password="Secure123", name="A")

    def test_name_too_long(self):
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError, match="at most 100"):
            UserCreate(email="test@example.com", password="Secure123", name="A" * 101)

    def test_invalid_email(self):
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", password="Secure123", name="Test")


class TestContentSchemas:
    def test_valid_post_create(self):
        from app.schemas.content import PostCreate
        post = PostCreate(platform="instagram", body="Hello world")
        assert post.platform == "instagram"

    def test_invalid_platform(self):
        from app.schemas.content import PostCreate
        with pytest.raises(ValidationError, match="platform"):
            PostCreate(platform="myspace", body="Hello")

    def test_invalid_content_type(self):
        from app.schemas.content import PostCreate
        with pytest.raises(ValidationError, match="content_type"):
            PostCreate(platform="instagram", content_type="invalid_type")

    def test_title_too_long(self):
        from app.schemas.content import PostCreate
        with pytest.raises(ValidationError, match="at most 500"):
            PostCreate(platform="instagram", title="A" * 501)

    def test_body_too_long(self):
        from app.schemas.content import PostCreate
        with pytest.raises(ValidationError, match="at most 10000"):
            PostCreate(platform="instagram", body="A" * 10001)

    def test_generate_request_invalid_platform(self):
        from app.schemas.content import ContentGenerateRequest
        with pytest.raises(ValidationError, match="platform"):
            ContentGenerateRequest(platform="invalid")

    def test_generate_request_num_variations_too_high(self):
        from app.schemas.content import ContentGenerateRequest
        with pytest.raises(ValidationError, match="between 1 and 10"):
            ContentGenerateRequest(platform="instagram", num_variations=11)

    def test_generate_request_num_variations_zero(self):
        from app.schemas.content import ContentGenerateRequest
        with pytest.raises(ValidationError, match="between 1 and 10"):
            ContentGenerateRequest(platform="instagram", num_variations=0)


class TestCampaignSchemas:
    def test_valid_campaign(self):
        from app.schemas.campaign import CampaignCreate
        campaign = CampaignCreate(name="Test Campaign", platform="instagram")
        assert campaign.platform == "instagram"

    def test_invalid_platform(self):
        from app.schemas.campaign import CampaignCreate
        with pytest.raises(ValidationError, match="platform"):
            CampaignCreate(name="Test", platform="myspace")

    def test_invalid_objective(self):
        from app.schemas.campaign import CampaignCreate
        with pytest.raises(ValidationError, match="objective"):
            CampaignCreate(name="Test", platform="instagram", objective="invalid")

    def test_name_too_long(self):
        from app.schemas.campaign import CampaignCreate
        with pytest.raises(ValidationError, match="at most 200"):
            CampaignCreate(name="A" * 201, platform="instagram")

    def test_generate_request_budget_negative(self):
        from app.schemas.campaign import CampaignGenerateRequest
        from decimal import Decimal
        with pytest.raises(ValidationError, match="greater than 0"):
            CampaignGenerateRequest(objective="awareness", budget=Decimal("-100"))

    def test_generate_request_budget_too_high(self):
        from app.schemas.campaign import CampaignGenerateRequest
        from decimal import Decimal
        with pytest.raises(ValidationError, match="at most 1,000,000"):
            CampaignGenerateRequest(objective="awareness", budget=Decimal("2000000"))


class TestChatSchemas:
    def test_valid_message(self):
        from app.schemas.chat import ChatMessage
        msg = ChatMessage(message="Hello")
        assert msg.message == "Hello"

    def test_empty_message(self):
        from app.schemas.chat import ChatMessage
        with pytest.raises(ValidationError, match="cannot be empty"):
            ChatMessage(message="   ")

    def test_message_too_long(self):
        from app.schemas.chat import ChatMessage
        with pytest.raises(ValidationError, match="at most 5000"):
            ChatMessage(message="A" * 5001)

    def test_invalid_report_type(self):
        from app.schemas.chat import ReportRequest
        with pytest.raises(ValidationError, match="must be one of"):
            ReportRequest(report_type="invalid")

    def test_valid_report_type(self):
        from app.schemas.chat import ReportRequest
        req = ReportRequest(report_type="weekly")
        assert req.report_type == "weekly"


class TestSocialSchemas:
    def test_valid_connect(self):
        from app.schemas.social import ConnectRequest
        req = ConnectRequest(platform="instagram", auth_code="abc", redirect_uri="https://example.com/callback")
        assert req.platform == "instagram"

    def test_invalid_platform(self):
        from app.schemas.social import ConnectRequest
        with pytest.raises(ValidationError, match="platform"):
            ConnectRequest(platform="myspace", auth_code="abc", redirect_uri="https://example.com")

    def test_invalid_redirect_uri(self):
        from app.schemas.social import ConnectRequest
        with pytest.raises(ValidationError, match="valid URL"):
            ConnectRequest(platform="instagram", auth_code="abc", redirect_uri="ftp://invalid")

    def test_empty_platforms_publish(self):
        from app.schemas.social import PublishRequest
        from uuid import uuid4
        with pytest.raises(ValidationError, match="At least one"):
            PublishRequest(post_id=uuid4(), platforms=[])


class TestRateLimiter:
    def test_allows_within_limit(self):
        from app.rate_limit import RateLimiter
        limiter = RateLimiter()
        from unittest.mock import MagicMock
        request = MagicMock()
        request.headers = {}
        request.client.host = "127.0.0.1"

        limiter.check(request, "test", max_requests=3, window_seconds=60)
        limiter.check(request, "test", max_requests=3, window_seconds=60)
        limiter.check(request, "test", max_requests=3, window_seconds=60)

    def test_blocks_over_limit(self):
        from app.rate_limit import RateLimiter
        from fastapi import HTTPException
        limiter = RateLimiter()
        from unittest.mock import MagicMock
        request = MagicMock()
        request.headers = {}
        request.client.host = "127.0.0.1"

        for _ in range(3):
            limiter.check(request, "test", max_requests=3, window_seconds=60)

        with pytest.raises(HTTPException) as exc_info:
            limiter.check(request, "test", max_requests=3, window_seconds=60)
        assert exc_info.value.status_code == 429
