"""Initial schema creation

Revision ID: 001_initial
Revises: 
Create Date: 2026-05-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Staff table (shared)
    op.create_table('staff',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('staff_code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(15), nullable=False),
        sa.Column('email', sa.String(150), nullable=True),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('joined_date', sa.Date(), nullable=False),
        sa.Column('aadhaar_number', sa.String(12), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('photo_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('staff_code'),
        sa.UniqueConstraint('phone'),
    )

    # Customers table (shared)
    op.create_table('customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('phone', sa.String(15), nullable=False),
        sa.Column('email', sa.String(150), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('aadhaar_number', sa.String(12), nullable=True),
        sa.Column('pan_number', sa.String(10), nullable=True),
        sa.Column('kyc_status', sa.String(20), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('anniversary_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone'),
    )

    # Vendors
    op.create_table('vendors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('phone', sa.String(15), nullable=False),
        sa.Column('email', sa.String(150), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('gstin', sa.String(15), nullable=True),
        sa.Column('pan_number', sa.String(10), nullable=True),
        sa.Column('bank_account', sa.String(30), nullable=True),
        sa.Column('bank_ifsc', sa.String(11), nullable=True),
        sa.Column('credit_limit', sa.Float(), nullable=True, default=0.0),
        sa.Column('outstanding_amount', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # Karigars
    op.create_table('karigars',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('phone', sa.String(15), nullable=True),
        sa.Column('specialty', sa.String(100), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('rate_per_gram', sa.Float(), nullable=True),
        sa.Column('outstanding_amount', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # Ornaments
    op.create_table('ornaments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_code', sa.String(30), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metal_type', sa.String(20), nullable=False),
        sa.Column('category', sa.String(10), nullable=False),
        sa.Column('gross_weight', sa.Float(), nullable=False),
        sa.Column('net_weight', sa.Float(), nullable=False),
        sa.Column('stone_weight', sa.Float(), nullable=True, default=0.0),
        sa.Column('stone_type', sa.String(100), nullable=True),
        sa.Column('stone_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('purity', sa.String(10), nullable=True),
        sa.Column('making_charge_type', sa.String(20), nullable=True, default='percent'),
        sa.Column('making_charge_value', sa.Float(), nullable=False),
        sa.Column('hallmark_charge', sa.Float(), nullable=True, default=0.0),
        sa.Column('other_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('karigar_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, default='in_stock'),
        sa.Column('photo_path', sa.String(500), nullable=True),
        sa.Column('barcode_path', sa.String(500), nullable=True),
        sa.Column('qr_path', sa.String(500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.ForeignKeyConstraint(['karigar_id'], ['karigars.id']),
        sa.ForeignKeyConstraint(['created_by'], ['staff.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tag_code'),
    )

    # Metal rates
    op.create_table('metal_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rate_date', sa.Date(), nullable=False),
        sa.Column('session', sa.String(15), nullable=False),
        sa.Column('gold_22k', sa.Float(), nullable=False),
        sa.Column('gold_18k', sa.Float(), nullable=False),
        sa.Column('gold_24k', sa.Float(), nullable=False),
        sa.Column('gold_14k', sa.Float(), nullable=True),
        sa.Column('gold_9k', sa.Float(), nullable=True),
        sa.Column('silver', sa.Float(), nullable=False),
        sa.Column('silver_925', sa.Float(), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['updated_by'], ['staff.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rate_date', 'session', name='uq_metal_rate_date_session'),
    )

    # Schemes
    op.create_table('schemes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('scheme_type', sa.String(10), nullable=False),
        sa.Column('duration_months', sa.Integer(), nullable=False),
        sa.Column('monthly_amount', sa.Float(), nullable=True),
        sa.Column('monthly_gold_grams', sa.Float(), nullable=True),
        sa.Column('bonus_month', sa.Boolean(), nullable=True, default=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('scheme_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_number', sa.String(30), nullable=False),
        sa.Column('scheme_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(15), nullable=True, default='active'),
        sa.Column('total_paid', sa.Float(), nullable=True, default=0.0),
        sa.Column('months_paid', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['scheme_id'], ['schemes.id']),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_number'),
    )

    op.create_table('scheme_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('gold_grams', sa.Float(), nullable=True),
        sa.Column('month_number', sa.Integer(), nullable=False),
        sa.Column('payment_mode', sa.String(20), nullable=False),
        sa.Column('receipt_number', sa.String(30), nullable=True),
        sa.Column('collected_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['scheme_accounts.id']),
        sa.ForeignKeyConstraint(['collected_by'], ['staff.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Rokar
    op.create_table('rokar_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('entry_type', sa.String(15), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.String(300), nullable=False),
        sa.Column('reference_id', sa.String(100), nullable=True),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['staff.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('bank_ledger',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_name', sa.String(100), nullable=False),
        sa.Column('account_number', sa.String(30), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('transaction_type', sa.String(20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.String(300), nullable=False),
        sa.Column('reference', sa.String(100), nullable=True),
        sa.Column('balance_after', sa.Float(), nullable=True),
        sa.Column('is_reconciled', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['staff.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('expenses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('category', sa.String(20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.String(300), nullable=False),
        sa.Column('payment_mode', sa.String(20), nullable=False),
        sa.Column('receipt_path', sa.String(500), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['staff.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Staff attendance
    op.create_table('staff_attendance_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('staff_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('log_time', sa.DateTime(), nullable=False),
        sa.Column('log_type', sa.String(10), nullable=False),
        sa.Column('session', sa.String(20), nullable=False),
        sa.Column('qr_code', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['staff_id'], ['staff.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('vendor_purchases',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('purchase_number', sa.String(30), nullable=False),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('purchase_date', sa.DateTime(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('amount_paid', sa.Float(), nullable=True, default=0.0),
        sa.Column('balance_due', sa.Float(), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=True),
        sa.Column('invoice_path', sa.String(500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.ForeignKeyConstraint(['created_by'], ['staff.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('purchase_number'),
    )


def downgrade() -> None:
    op.drop_table('vendor_purchases')
    op.drop_table('staff_attendance_logs')
    op.drop_table('expenses')
    op.drop_table('bank_ledger')
    op.drop_table('rokar_entries')
    op.drop_table('scheme_transactions')
    op.drop_table('scheme_accounts')
    op.drop_table('schemes')
    op.drop_table('metal_rates')
    op.drop_table('ornaments')
    op.drop_table('karigars')
    op.drop_table('vendors')
    op.drop_table('customers')
    op.drop_table('staff')
