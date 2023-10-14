from src.config import conf
from src.db.database import create_async_engine

engine = create_async_engine(conf.db.build_connection_str())
