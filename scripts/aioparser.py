import asyncio
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.config import DatabaseConfig
from src.db.database import Database, create_async_engine, create_session_maker
from src.db.models import Participant

path_to_plan = Path(__file__).with_name("aioparser.xlsx")


async def parse(db: Database):
    print("Парсинг номинаций")
    df = pd.read_excel(path_to_plan.absolute(), sheet_name="nominations")
    df.replace({np.nan: None}, inplace=True)
    nominations_count = 0
    for _index, row in df.iterrows():
        nomination = await db.nomination.get(row["id"])
        if nomination:
            print(f"Номинация {row['id']} уже существует")
        else:
            votable = bool(row["votable"])
            nomination = await db.nomination.new(
                nomination_id=row["id"], title=row["title"], votable=votable
            )
            await db.session.flush([nomination])
            print(f"Номинация {row['id']} добавлена в БД")
            nominations_count += 1
    print("Парсинг участников")
    df = pd.read_excel(path_to_plan.absolute(), sheet_name="participants")
    df.replace({np.nan: None}, inplace=True)
    participants_count = 0
    for _index, row in df.iterrows():
        participant = await db.participant.get_by_where(
            Participant.title == row["title"]
        )
        if participant:
            print(f"Участник {row['title'][0:40]}... уже существует")
        else:
            nomination = await db.nomination.get(row["nomination_id"])
            if nomination:
                participant = await db.participant.new(
                    title=row["title"], nomination_id=nomination.id
                )
                await db.session.flush([participant])
                print(f"Участник {row['title'][0:40]}... добавлен в БД")
                participants_count += 1
            else:
                print(
                    f"Некорректно указана номинация для "
                    f"{row['title'][0:40]}..., пропускаем парсинг"
                )
    print("Парсинг билетов")
    df = pd.read_excel(path_to_plan.absolute(), sheet_name="tickets")
    df.replace({np.nan: None}, inplace=True)
    tickets_count = 0
    for _index, row in df.iterrows():
        ticket = await db.ticket.get(row["id"])
        if ticket:
            print("Билет с таким номером уже существует")
        else:
            ticket = await db.ticket.new(id=row["id"], role=row["role"])
            await db.session.flush([ticket])
            print(f"Билет {row['id']} добавлен в БД")
            tickets_count += 1
    await db.session.commit()
    return nominations_count, participants_count, tickets_count


async def main(session_pool):
    async with session_pool() as session:
        db = Database(session)
        print("Начинаем парсинг aioparser.xlsx...")
        nominations_count, participants_count, tickets_count = await parse(db)
        print(
            f"Парсинг завершён! Было добавлено {nominations_count!s} "
            f"новых номинаций, {participants_count} новых участников "
            f"и {tickets_count} новых билетов"
        )
        pass
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
