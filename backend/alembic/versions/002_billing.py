"""Pakka and Kacha billing tables

Revision ID: 002_billing
Revises: 001_initial
Create Date: 2026-05-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_billing'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def _create_pakka_tables():
    op.create_table('pakka_sales',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bill_number', sa.String(30), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('salesman_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_date', sa.DateTime(), nullable=False),
        sa.Column('metal_rate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('gst_rate', sa.Float(), nullable=False, default=0.03),
        sa.Column('gst_amount', sa.Float(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('payment_mode', sa.String(20), nullable=False),
        sa.Column('amount_paid', sa.Float(), nullable=False),
        sa.Column('balance_due', sa.Float(), nullable=True, default=0.0),
        sa.Column('status', sa.String(15), nullable=True, default='active'),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bill_number'),
    )

    op.create_table('pakka_sale_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ornament_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_code', sa.String(30), nullable=False),
        sa.Column('ornament_name', sa.String(200), nullable=False),
        sa.Column('metal_type', sa.String(20), nullable=False),
        sa.Column('net_weight', sa.Float(), nullable=False),
        sa.Column('gold_rate', sa.Float(), nullable=False),
        sa.Column('gold_value', sa.Float(), nullable=False),
        sa.Column('making_charge_type', sa.String(20), nullable=False),
        sa.Column('making_charge_value', sa.Float(), nullable=False),
        sa.Column('making_charge_amount', sa.Float(), nullable=False),
        sa.Column('stone_value', sa.Float(), nullable=True, default=0.0),
        sa.Column('hallmark_charge', sa.Float(), nullable=True, default=0.0),
        sa.Column('other_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('item_subtotal', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['sale_id'], ['pakka_sales.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def _create_kacha_tables():
    op.create_table('kacha_sales',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bill_number', sa.String(30), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('salesman_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_date', sa.DateTime(), nullable=False),
        sa.Column('metal_rate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('old_gold_value', sa.Float(), nullable=True, default=0.0),
        sa.Column('old_gold_weight', sa.Float(), nullable=True, default=0.0),
        sa.Column('old_gold_purity', sa.String(10), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('payment_mode', sa.String(20), nullable=False),
        sa.Column('amount_paid', sa.Float(), nullable=False),
        sa.Column('balance_due', sa.Float(), nullable=True, default=0.0),
        sa.Column('status', sa.String(15), nullable=True, default='active'),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bill_number'),
    )

    op.create_table('kacha_sale_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ornament_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_code', sa.String(30), nullable=False),
        sa.Column('ornament_name', sa.String(200), nullable=False),
        sa.Column('metal_type', sa.String(20), nullable=False),
        sa.Column('net_weight', sa.Float(), nullable=False),
        sa.Column('gold_rate', sa.Float(), nullable=False),
        sa.Column('gold_value', sa.Float(), nullable=False),
        sa.Column('making_charge_type', sa.String(20), nullable=False),
        sa.Column('making_charge_value', sa.Float(), nullable=False),
        sa.Column('making_charge_amount', sa.Float(), nullable=False),
        sa.Column('stone_value', sa.Float(), nullable=True, default=0.0),
        sa.Column('hallmark_charge', sa.Float(), nullable=True, default=0.0),
        sa.Column('other_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('item_subtotal', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['sale_id'], ['kacha_sales.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def upgrade() -> None:
    _create_pakka_tables()
    _create_kacha_tables()


def downgrade() -> None:
    op.drop_table('kacha_sale_items')
    op.drop_table('kacha_sales')
    op.drop_table('pakka_sale_items')
    op.drop_table('pakka_sales')
