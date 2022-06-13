"""empty message

Revision ID: 6078a793c5e6
Revises: 06eb7e54eb56
Create Date: 2022-06-11 18:58:30.213557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6078a793c5e6'
down_revision = '06eb7e54eb56'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe', sa.Column('name', sa.String(length=75), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipe', 'name')
    # ### end Alembic commands ###
