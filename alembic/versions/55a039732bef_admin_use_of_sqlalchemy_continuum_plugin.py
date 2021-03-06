"""admin: use of sqlalchemy continuum plugin

Revision ID: 55a039732bef
Revises: 15ce4717213
Create Date: 2018-04-24 18:14:06.813663

"""

# revision identifiers, used by Alembic.
revision = '55a039732bef'
down_revision = '15ce4717213'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_history')
    op.drop_table('columnmodel_history')
    op.drop_table('meta_history')
    op.drop_table('relationmodel_history')
    op.drop_table('tablemodel_history')

    table_list = ('user',
                  'tablemodel',
                  'columnmodel',
                  'meta',
                  'relationmodel')

    # rename all tables to table_copy
    for tab in table_list:
        op.rename_table(tab, '%s_copy' % tab)

    op.create_table('columnmodel',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('record_date', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(), nullable=True),
    sa.Column('last_name', sa.VARCHAR(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.Column('username', sa.VARCHAR(), nullable=True),
    sa.Column('password_hash', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('meta',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('description', sa.VARCHAR(), nullable=True),
    sa.Column('meta_type', sa.VARCHAR(), nullable=True),
    sa.Column('is_deleted', sa.BOOLEAN(), nullable=True),
    sa.Column('record_date', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('meta_table_id', sa.INTEGER(), nullable=True),
    sa.Column('meta_column_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['meta_column_id'], [u'columnmodel.id'], ),
    sa.ForeignKeyConstraint(['meta_table_id'], [u'tablemodel.id'], ),
    sa.ForeignKeyConstraint(['user_id'], [u'user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('relationmodel',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('record_date', sa.DATETIME(), nullable=True),
    sa.Column('is_deleted', sa.BOOLEAN(), nullable=True),
    sa.Column('columnl_id', sa.INTEGER(), nullable=True),
    sa.Column('columnr_id', sa.INTEGER(), nullable=True),
    sa.Column('tablel_id', sa.INTEGER(), nullable=True),
    sa.Column('tabler_id', sa.INTEGER(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['columnl_id'], [u'columnmodel.id'], ),
    sa.ForeignKeyConstraint(['columnr_id'], [u'columnmodel.id'], ),
    sa.ForeignKeyConstraint(['tablel_id'], [u'tablemodel.id'], ),
    sa.ForeignKeyConstraint(['tabler_id'], [u'tablemodel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tablemodel',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('record_date', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    for tab in table_list:
        tab_copy = '%s_copy' % tab
        op.execute(table_copy_str(tab, tab_copy))
        op.drop_table(tab_copy)

    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('version', sa.INTEGER(), nullable=True))
    op.add_column('tablemodel', sa.Column('version', sa.INTEGER(), nullable=True))
    op.add_column('relationmodel', sa.Column('version', sa.INTEGER(), nullable=True))
    op.add_column('meta', sa.Column('version', sa.INTEGER(), nullable=True))
    op.add_column('columnmodel', sa.Column('version', sa.INTEGER(), nullable=True))
    op.create_table('tablemodel_history',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('record_date', sa.DATETIME(), nullable=True),
    sa.Column('version', sa.INTEGER(), nullable=False),
    sa.Column('changed', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'version')
    )
    op.create_table('relationmodel_history',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('record_date', sa.DATETIME(), nullable=True),
    sa.Column('is_deleted', sa.BOOLEAN(), nullable=True),
    sa.Column('columnl_id', sa.INTEGER(), nullable=True),
    sa.Column('columnr_id', sa.INTEGER(), nullable=True),
    sa.Column('tablel_id', sa.INTEGER(), nullable=True),
    sa.Column('tabler_id', sa.INTEGER(), nullable=True),
    sa.Column('version', sa.INTEGER(), nullable=False),
    sa.Column('changed', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'version')
    )
    op.create_table('meta_history',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('description', sa.VARCHAR(), nullable=True),
    sa.Column('meta_type', sa.VARCHAR(), nullable=True),
    sa.Column('is_deleted', sa.BOOLEAN(), nullable=True),
    sa.Column('record_date', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('meta_table_id', sa.INTEGER(), nullable=True),
    sa.Column('meta_column_id', sa.INTEGER(), nullable=True),
    sa.Column('version', sa.INTEGER(), nullable=False),
    sa.Column('changed', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'version')
    )
    op.create_table('columnmodel_history',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('record_date', sa.DATETIME(), nullable=True),
    sa.Column('version', sa.INTEGER(), nullable=False),
    sa.Column('changed', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'version')
    )
    op.create_table('user_history',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(), nullable=True),
    sa.Column('last_name', sa.VARCHAR(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.Column('username', sa.VARCHAR(), nullable=True),
    sa.Column('password_hash', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.Column('version', sa.INTEGER(), nullable=False),
    sa.Column('changed', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'version')
    )
    ### end Alembic commands ###

def table_copy_str(tab, tab_copy):

    '''
    copy data from table tab_copy to table tab
    '''


    if tab == 'user':

        return '''
        INSERT INTO %s (id, first_name, last_name, email, username, password_hash, is_active)
            SELECT
                id,
                first_name,
                last_name,
                email,
                username,
                password_hash,
                is_active
            FROM %s
        ''' % (tab, tab_copy)

    if tab == 'tablemodel' or tab == 'columnmodel':

        return '''
        INSERT INTO %s (id, name, record_date)
            SELECT
                id,
                name,
                record_date
            FROM %s
        ''' % (tab, tab_copy)

    if tab == 'meta':

        return '''
        INSERT INTO %s (id, description, meta_type, is_deleted, record_date, user_id, meta_table_id, meta_column_id)
            SELECT
                id,
                description,
                meta_type,
                is_deleted,
                record_date,
                user_id,
                meta_table_id,
                meta_column_id
            FROM %s
        ''' % (tab, tab_copy)


    if tab == 'relationmodel':

        return '''
        INSERT INTO %s (id, record_date, is_deleted, columnl_id, columnr_id, tablel_id, tabler_id, user_id)
            SELECT
                id,
                record_date,
                is_deleted,
                columnl_id,
                columnr_id,
                tablel_id,
                tabler_id,
                user_id
            FROM %s
        ''' % (tab, tab_copy)
