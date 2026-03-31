import sys
from sqlalchemy import create_engine
from app.core.config import settings

try:
    engine = create_engine(settings.DATABASE_URL)
    conn = engine.connect()
    print("SUCCESS: Connected to DB!")
    conn.close()
except Exception as e:
    print(f"FAILED WITH EXC: {repr(e)}")
