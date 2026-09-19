from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial_sqlite'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create tables needed for development (simplified)
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
    )
    op.create_table(
        'study_areas',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('geom', sa.Text(), nullable=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
    )
    op.create_table(
        'datasets',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('study_area_id', sa.Integer(), sa.ForeignKey('study_areas.id'), nullable=False),
    )

def downgrade():
    op.drop_table('datasets')
    op.drop_table('study_areas')
    op.drop_table('projects')
