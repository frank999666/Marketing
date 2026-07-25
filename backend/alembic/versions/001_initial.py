"""Initial migration

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Companies
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), unique=True, index=True),
        sa.Column('plan', sa.String(50), server_default='free'),
        sa.Column('brand_config', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    # User-Company association
    op.create_table(
        'user_companies',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), primary_key=True),
        sa.Column('role', sa.String(50), server_default='member'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Brand Profiles
    op.create_table(
        'brand_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), unique=True, nullable=False),
        sa.Column('industry', sa.String(100)),
        sa.Column('tone', sa.String(100)),
        sa.Column('values', postgresql.ARRAY(sa.Text)),
        sa.Column('target_audience', sa.Text),
        sa.Column('colors', postgresql.JSONB, server_default='{}'),
        sa.Column('fonts', postgresql.JSONB, server_default='{}'),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('guidelines', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Posts
    op.create_table(
        'posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('content_type', sa.String(50)),
        sa.Column('title', sa.String(255)),
        sa.Column('body', sa.Text),
        sa.Column('hashtags', postgresql.ARRAY(sa.Text)),
        sa.Column('media_urls', postgresql.JSONB, server_default='[]'),
        sa.Column('cta', sa.String(255)),
        sa.Column('image_url', sa.String(500)),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('scheduled_at', sa.DateTime),
        sa.Column('published_at', sa.DateTime),
        sa.Column('post_id_external', sa.String(255)),
        sa.Column('metrics', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Content Calendar
    op.create_table(
        'content_calendar',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id')),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('time', sa.Time),
        sa.Column('platform', sa.String(50)),
        sa.Column('status', sa.String(50), server_default='planned'),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Social Accounts
    op.create_table(
        'social_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('account_id', sa.String(255)),
        sa.Column('access_token', sa.Text),
        sa.Column('refresh_token', sa.Text),
        sa.Column('token_expires_at', sa.DateTime),
        sa.Column('username', sa.String(255)),
        sa.Column('profile_data', postgresql.JSONB, server_default='{}'),
        sa.Column('connected_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('last_synced', sa.DateTime),
    )

    # Analytics Snapshots
    op.create_table(
        'analytics_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('social_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('social_accounts.id')),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id'), nullable=True),
        sa.Column('metric_type', sa.String(50), nullable=False),
        sa.Column('metric_value', sa.BigInteger, server_default='0'),
        sa.Column('snapshot_date', sa.Date, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Analytics Alerts
    op.create_table(
        'analytics_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('alert_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(50), server_default='warning'),
        sa.Column('title', sa.String(255)),
        sa.Column('message', sa.Text),
        sa.Column('explanation', sa.Text),
        sa.Column('evidence', postgresql.JSONB, server_default='{}'),
        sa.Column('suggested_actions', postgresql.JSONB, server_default='[]'),
        sa.Column('data', postgresql.JSONB, server_default='{}'),
        sa.Column('acknowledged', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Ad Campaigns
    op.create_table(
        'ad_campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('objective', sa.String(100)),
        sa.Column('budget', sa.Numeric(10, 2)),
        sa.Column('daily_budget', sa.Numeric(10, 2)),
        sa.Column('audience_config', postgresql.JSONB, server_default='{}'),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('approved', sa.Boolean, server_default='false'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('start_date', sa.DateTime),
        sa.Column('end_date', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Ad Creatives
    op.create_table(
        'ad_creatives',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ad_campaigns.id'), nullable=False),
        sa.Column('copy', sa.Text),
        sa.Column('headline', sa.String(255)),
        sa.Column('description', sa.Text),
        sa.Column('image_url', sa.String(500)),
        sa.Column('video_url', sa.String(500)),
        sa.Column('cta', sa.String(100)),
        sa.Column('variant', sa.String(10)),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Reports
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('period_start', sa.Date, nullable=False),
        sa.Column('period_end', sa.Date, nullable=False),
        sa.Column('content', postgresql.JSONB, server_default='{}'),
        sa.Column('file_url', sa.String(500)),
        sa.Column('status', sa.String(50), server_default='generated'),
        sa.Column('generated_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_table('ad_creatives')
    op.drop_table('ad_campaigns')
    op.drop_table('analytics_alerts')
    op.drop_table('analytics_snapshots')
    op.drop_table('social_accounts')
    op.drop_table('content_calendar')
    op.drop_table('posts')
    op.drop_table('brand_profiles')
    op.drop_table('user_companies')
    op.drop_table('companies')
    op.drop_table('users')
