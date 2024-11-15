"""Change month to Integer in employee_monthly_salary

Revision ID: 8fa3afcfc0a5
Revises: 3b1d3c6523b1
Create Date: 2024-11-15 16:30:52.490774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fa3afcfc0a5'
down_revision = '3b1d3c6523b1'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    op.alter_column(
        "employee_monthly_salary",
        "month",
        existing_type=sa.String(),  # Replace with the actual type of the column before the change
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="month::integer"  # Add this line
    )

def downgrade():
    op.alter_column(
        "employee_monthly_salary",
        "month",
        existing_type=sa.Integer(),
        type_=sa.String(),  # Replace with the actual type of the column before the change
        existing_nullable=True
    )

