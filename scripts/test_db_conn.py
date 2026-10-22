import asyncio
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.infrastructure.db import init_db, engine
from sqlalchemy import text


async def main():
    print("Connecting to database and initializing schema...")
    await init_db()
    async with engine.connect() as conn:
        res = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;")
        )
        tables = [row[0] for row in res.fetchall()]
        print("Schema successfully initialized!")
        print("Tables in Neon database:")
        for t in tables:
            print(f"  - {t}")


if __name__ == "__main__":
    asyncio.run(main())
