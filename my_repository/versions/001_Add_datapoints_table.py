from sqlalchemy import *
from migrate import *

from sqlalchemy import Table, Column, Integer, String, MetaData
meta = MetaData()

datapoints = Table(
    'datapoints', meta,
    Column('id', Integer, primary_key=True),
    Column('latitude', String(20)),
    Column('longitude', String(20)),
    Column('numero', Integer),
    Column('bairro', String(50)),
    Column('cidade', String(30)),
    Column('estado', String(30)),
    Column('cep', Integer),
    Column('pais', String(20)),
    Column('pais_codigo', String(2)),
    Column('rua', String(100)),
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    datapoints.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    datapoints.drop()
