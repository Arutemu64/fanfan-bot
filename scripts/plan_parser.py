import asyncio
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import text

from scripts.config import DatabaseConfig
from src.db.database import Database, create_async_engine, create_session_maker

path_to_plan = Path(__file__).with_name("technical_plan.csv")


async def clean_db(db: Database):
    print("Удаляем голоса...")
    nominations = await db.nomination.get_many(True, limit=1000)
    for nomination in nominations:
        await db.session.delete(nomination)
    await db.session.execute(text("ALTER SEQUENCE votes_id_seq RESTART WITH 1"))
    await db.session.commit()

    print("Удаляем события...")
    events = await db.event.get_many(True, limit=1000)
    for event in events:
        await db.session.delete(event)
    await db.session.execute(text("ALTER SEQUENCE schedule_id_seq RESTART WITH 1"))
    await db.session.commit()

    print("Удаляем участников...")
    participants = await db.participant.get_many(True, limit=1000)
    for participant in participants:
        await db.session.delete(participant)
    await db.session.execute(text("ALTER SEQUENCE participants_id_seq RESTART WITH 1"))
    await db.session.commit()

    print("Удаляем номинации...")
    nominations = await db.nomination.get_many(True, limit=1000)
    for nomination in nominations:
        await db.session.delete(nomination)
    await db.session.commit()


async def parse_plan(db: Database):
    df = pd.read_csv(path_to_plan.absolute())
    df["next_code"] = df["code"].shift(-1)
    df.replace({np.nan: None}, inplace=True)
    for index, row in df.iterrows():
        if row["code"] is not None:  # participant
            participant = await db.participant.new(
                title=row["voting_title"], nomination_id=row["code"]
            )
            await db.session.flush([participant])
            event = await db.event.new(participant_id=participant.id)
            await db.session.flush([event])
        elif row["code"] is None and row["next_code"] is not None:  # nomination
            nomination = await db.nomination.new(
                nomination_id=row["next_code"], title=row["info"]
            )
            await db.session.flush([nomination])
        elif row["code"] is None and row["next_code"] is None:  # schedule entry
            event = await db.event.new(title=row["info"])
            await db.session.flush([event])
    await db.session.commit()


async def main(session_pool):
    async with session_pool() as session:
        db = Database(session)
        print("Очищаем БД...")
        await clean_db(db)
        print("БД очищена! Переходим к парсингу плана...")
        await parse_plan(db)
        participants_count = await db.participant.count(True)
        events_count = await db.event.count(True)
        nominations_count = await db.nomination.count(True)
        print(f"Парсинг завершён! Было добавлено {str(nominations_count)} номинации, "
              f"{str(participants_count)} участников и {str(events_count)} событий!")
    return


if __name__ == "__main__":
    try:
        db_config = DatabaseConfig()
        print(db_config.host)
        engine = create_async_engine(db_config.build_connection_str())
        print(engine.url)
        session_pool = create_session_maker(engine)
        asyncio.run(main(session_pool))
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
