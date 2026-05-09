from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.db.session import Base, PakkaBase, KachaBase, shared_engine, pakka_engine, kacha_engine
# Import all models so metadata is populated
from app.models import staff, customer, ornament, metal_rate, billing, scheme, rokar, vendor

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# We'll run migrations on all three databases
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    for engine, metadata in [
        (shared_engine, Base.metadata),
        (pakka_engine, PakkaBase.metadata),
        (kacha_engine, KachaBase.metadata),
    ]:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=metadata)
            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
