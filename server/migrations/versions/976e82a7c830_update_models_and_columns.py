"""Update schema to match new models columns

Revision ID: 976e82a7c830
Revises: 
Create Date: 2024-08-08 19:15:03.963752

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '976e82a7c830'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table changes
    op.alter_column('users', 'worker_id', existing_type=sa.INTEGER(), type_=sa.String(length=50), nullable=True)
    op.drop_column('users', 'username')
    op.create_unique_constraint(None, 'users', ['worker_id'])

    # Records table changes
    op.add_column('records', sa.Column('public_id', sa.String(length=40), nullable=True))
    op.add_column('records', sa.Column('record_type', sa.String(length=20), nullable=True))
    op.add_column('records', sa.Column('user_public_id', sa.String(length=40), nullable=True))
    
    # Update existing rows with UUIDs
    op.execute("UPDATE records SET public_id = gen_random_uuid()::text WHERE public_id IS NULL")
    op.execute("UPDATE records SET record_type = 'red-flag' WHERE record_type IS NULL")  # Default to 'red-flag', adjust as needed
    op.execute("UPDATE records SET user_public_id = (SELECT public_id FROM users WHERE users.id = records.user_id) WHERE user_public_id IS NULL")
    
    op.alter_column('records', 'public_id', nullable=False)
    op.alter_column('records', 'record_type', nullable=False)
    op.alter_column('records', 'user_public_id', nullable=False)
    
    op.create_unique_constraint(None, 'records', ['public_id'])
    op.drop_constraint('records_user_id_fkey', 'records', type_='foreignkey')
    op.create_foreign_key(None, 'records', 'users', ['user_public_id'], ['public_id'])
    op.drop_column('records', 'user_id')

def downgrade():
    # Records table changes
    op.add_column('records', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'records', type_='foreignkey')
    op.create_foreign_key('records_user_id_fkey', 'records', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'records', type_='unique')
    op.drop_column('records', 'user_public_id')
    op.drop_column('records', 'record_type')
    op.drop_column('records', 'public_id')

    # Users table changes
    op.add_column('users', sa.Column('username', sa.VARCHAR(length=80), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='unique')
    op.alter_column('users', 'worker_id', existing_type=sa.String(length=50), type_=sa.INTEGER(), nullable=True)