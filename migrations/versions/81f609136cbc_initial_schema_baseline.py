
"""initial schema baseline

Revision ID: 81f609136cbc
Revises:
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '81f609136cbc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(150), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        
    )

    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Jobs
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(150), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('location', sa.String(100), nullable=False),
        sa.Column('employment_type', sa.String(50), nullable=False),
        sa.Column('experience_level', sa.String(50), nullable=False),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('recruiter_id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['recruiter_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_jobs_id', 'jobs', ['id'], unique=False)

    # Applications
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True
        ),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id']),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        'ix_applications_id',
        'applications',
        ['id'],
        unique=False
    )

    # Candidate Profiles
    op.create_table(
        'candidate_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('headline', sa.String(150), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('skills', sa.Text(), nullable=True),
        sa.Column('education', sa.Text(), nullable=True),
        sa.Column('experience', sa.Text(), nullable=True),
        sa.Column('resume_path', sa.String(255), nullable=True),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    op.create_index(
        'ix_candidate_profiles_id',
        'candidate_profiles',
        ['id'],
        unique=False
    )

    # Notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(150), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(50), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        'ix_notifications_id',
        'notifications',
        ['id'],
        unique=False
    )

    op.create_index(
        'ix_notifications_user_id',
        'notifications',
        ['user_id'],
        unique=False
    )


def downgrade() -> None:

    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_index('ix_notifications_id', table_name='notifications')
    op.drop_table('notifications')

    op.drop_index('ix_candidate_profiles_id', table_name='candidate_profiles')
    op.drop_table('candidate_profiles')

    op.drop_index('ix_applications_id', table_name='applications')
    op.drop_table('applications')

    op.drop_index('ix_jobs_id', table_name='jobs')
    op.drop_table('jobs')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
