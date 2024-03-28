"""empty message

Revision ID: 3095d43c54fb
Revises: 
Create Date: 2024-03-28 13:09:14.874008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3095d43c54fb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('is_confirmed', sa.Boolean(), nullable=True),
    sa.Column('confirmed_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('parent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.Column('phone_number', sa.String(length=15), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('age_range', sa.String(length=20), nullable=True),
    sa.Column('subject_area', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('local_government', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('subscriptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan', sa.String(length=50), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('remaining_usages', sa.Integer(), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('paystack_subscription_id', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tutor',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('address', sa.String(length=200), nullable=True),
    sa.Column('phone_number', sa.String(length=15), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('education_qualification', sa.String(length=50), nullable=True),
    sa.Column('interest', sa.Text(), nullable=True),
    sa.Column('subjects', sa.String(length=200), nullable=True),
    sa.Column('past_experience', sa.Boolean(), nullable=True),
    sa.Column('experience_years', sa.String(length=20), nullable=True),
    sa.Column('experience_description', sa.Text(), nullable=True),
    sa.Column('interest_join', sa.Text(), nullable=True),
    sa.Column('languages', sa.Text(), nullable=True),
    sa.Column('availability', sa.String(length=50), nullable=True),
    sa.Column('teaching_mode', sa.String(length=50), nullable=True),
    sa.Column('student_level', sa.String(length=50), nullable=True),
    sa.Column('source', sa.String(length=50), nullable=True),
    sa.Column('confirmation_name', sa.String(length=100), nullable=True),
    sa.Column('fee_paid', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('photo_data', sa.LargeBinary(), nullable=True),
    sa.Column('photo_filename', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('tutorfeepayment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tutor_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('payment_date', sa.Date(), nullable=False),
    sa.Column('paystack_tutorfeepayment_id', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['tutor_id'], ['tutor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tutorfeepayment')
    op.drop_table('tutor')
    op.drop_table('subscriptions')
    op.drop_table('parent')
    op.drop_table('users')
    # ### end Alembic commands ###