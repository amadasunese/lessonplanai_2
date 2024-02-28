"""empty message

Revision ID: b8ced1855777
Revises: d48acd9cdc08
Create Date: 2024-02-24 22:22:28.467892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8ced1855777'
down_revision = 'd48acd9cdc08'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tutor', sa.Column('photo_data', sa.LargeBinary(), nullable=True))
    op.add_column('tutor', sa.Column('photo_filename', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tutor', 'photo_filename')
    op.drop_column('tutor', 'photo_data')
    # ### end Alembic commands ###