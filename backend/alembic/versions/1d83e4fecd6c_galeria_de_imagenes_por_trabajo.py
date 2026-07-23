"""galería de imágenes por trabajo (elimina tipo/rol fijos)

Revision ID: 1d83e4fecd6c
Revises: 605a0c7e99b0
Create Date: 2026-07-23 03:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1d83e4fecd6c'
down_revision: Union[str, None] = '605a0c7e99b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    etiqueta_enum = sa.Enum('antes', 'despues', name='etiquetaimagen')
    etiqueta_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('trabajo_imagenes', sa.Column('orden', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('trabajo_imagenes', sa.Column('etiqueta', etiqueta_enum, nullable=True))

    op.execute(
        "UPDATE trabajo_imagenes SET etiqueta = rol::text::etiquetaimagen WHERE rol::text IN ('antes', 'despues')"
    )
    op.execute("UPDATE trabajo_imagenes SET orden = 1 WHERE rol::text = 'despues'")

    op.drop_constraint('uq_trabajo_imagen_rol', 'trabajo_imagenes', type_='unique')
    op.drop_column('trabajo_imagenes', 'rol')
    op.alter_column('trabajo_imagenes', 'orden', server_default=None)

    op.drop_column('trabajos', 'tipo')

    op.execute('DROP TYPE IF EXISTS rolimagen')
    op.execute('DROP TYPE IF EXISTS tipotrabajo')


def downgrade() -> None:
    tipo_enum = sa.Enum('antes_despues', 'foto', name='tipotrabajo')
    tipo_enum.create(op.get_bind(), checkfirst=True)
    rol_enum = sa.Enum('antes', 'despues', 'foto', name='rolimagen')
    rol_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('trabajos', sa.Column('tipo', tipo_enum, nullable=True))
    op.execute("UPDATE trabajos SET tipo = 'foto'")
    op.alter_column('trabajos', 'tipo', nullable=False)

    op.add_column('trabajo_imagenes', sa.Column('rol', rol_enum, nullable=True))
    op.execute("UPDATE trabajo_imagenes SET rol = etiqueta::text::rolimagen WHERE etiqueta IS NOT NULL")
    op.execute("UPDATE trabajo_imagenes SET rol = 'foto' WHERE rol IS NULL")
    op.alter_column('trabajo_imagenes', 'rol', nullable=False)

    op.create_unique_constraint('uq_trabajo_imagen_rol', 'trabajo_imagenes', ['trabajo_id', 'rol'])
    op.drop_column('trabajo_imagenes', 'etiqueta')
    op.drop_column('trabajo_imagenes', 'orden')

    op.execute('DROP TYPE IF EXISTS etiquetaimagen')
