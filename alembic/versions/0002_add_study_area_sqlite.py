from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_study_area_sqlite'
down_revision = '0001_initial_sqlite'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'study_areas',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        # Store geometry as WKT text for SQLite compatibility
        sa.Column('geom', sa.Text(), nullable=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
    )

def downgrade():
    op.drop_table('study_areas')
