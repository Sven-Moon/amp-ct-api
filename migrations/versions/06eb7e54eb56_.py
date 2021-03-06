"""empty message

Revision ID: 06eb7e54eb56
Revises: 
Create Date: 2022-06-11 15:01:03.274774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06eb7e54eb56'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ingredient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('image', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.String(length=40), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=40), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('token', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('recipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('prep_time', sa.Integer(), nullable=True),
    sa.Column('cook_time', sa.Integer(), nullable=True),
    sa.Column('instructions', sa.String(length=3000), nullable=True),
    sa.Column('category', sa.String(length=30), nullable=True),
    sa.Column('meal_types', sa.Integer(), nullable=True),
    sa.Column('last_made', sa.DateTime(), nullable=True),
    sa.Column('image', sa.String(length=500), nullable=True),
    sa.Column('scheduled', sa.Boolean(), nullable=True),
    sa.Column('fixed_schedule', sa.Boolean(), nullable=True),
    sa.Column('fixed_period', sa.SmallInteger(), nullable=True),
    sa.Column('rating', sa.SmallInteger(), nullable=True),
    sa.Column('rating_count', sa.SmallInteger(), nullable=True),
    sa.Column('created_by', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('schedule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=100), nullable=True),
    sa.Column('veg_freq', sa.SmallInteger(), nullable=True),
    sa.Column('pork_freq', sa.SmallInteger(), nullable=True),
    sa.Column('chicken_freq', sa.SmallInteger(), nullable=True),
    sa.Column('beef_freq', sa.SmallInteger(), nullable=True),
    sa.Column('fish_freq', sa.SmallInteger(), nullable=True),
    sa.Column('auto_made', sa.Boolean(), nullable=True),
    sa.Column('store_trip_method', sa.SmallInteger(), nullable=True),
    sa.Column('store_days_btwn', sa.SmallInteger(), nullable=True),
    sa.Column('store_trip_days', sa.SmallInteger(), nullable=True),
    sa.Column('store_meal_position', sa.String(length=10), nullable=True),
    sa.Column('plan_ahead_days', sa.SmallInteger(), nullable=True),
    sa.Column('next_store_trip', sa.DateTime(), nullable=True),
    sa.Column('plan_breakfast', sa.Boolean(), nullable=True),
    sa.Column('plan_lunch', sa.Boolean(), nullable=True),
    sa.Column('plan_dinner', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shopping_list',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=100), nullable=True),
    sa.Column('item_name', sa.String(length=50), nullable=False),
    sa.Column('item_qty', sa.SmallInteger(), nullable=True),
    sa.Column('item_uom', sa.String(length=10), nullable=True),
    sa.Column('crossed_off', sa.Boolean(), nullable=True),
    sa.Column('staple', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('day',
    sa.Column('user_id', sa.String(length=100), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('breakfast_recipe_id', sa.Integer(), nullable=True),
    sa.Column('lunch_recipe_id', sa.Integer(), nullable=True),
    sa.Column('dinner_recipe_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['breakfast_recipe_id'], ['recipe.id'], ),
    sa.ForeignKeyConstraint(['dinner_recipe_id'], ['recipe.id'], ),
    sa.ForeignKeyConstraint(['lunch_recipe_id'], ['recipe.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'date')
    )
    op.create_table('recipe_box',
    sa.Column('user_id', sa.String(length=100), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('custom_instr', sa.String(length=3000), nullable=True),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'recipe_id')
    )
    op.create_table('recipe_ingredient',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.SmallInteger(), nullable=True),
    sa.Column('uom', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredient.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.PrimaryKeyConstraint('recipe_id', 'ingredient_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipe_ingredient')
    op.drop_table('recipe_box')
    op.drop_table('day')
    op.drop_table('shopping_list')
    op.drop_table('schedule')
    op.drop_table('recipe')
    op.drop_table('user')
    op.drop_table('ingredient')
    # ### end Alembic commands ###
