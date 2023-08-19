import asyncio
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import text

from scripts.config import DatabaseConfig
from src.db.database import Database, create_async_engine, create_session_maker
from src.db.models import Nomination, Participant

path_to_plan = Path(__file__).with_name("technical_plan.csv")


async def clean_schedule(db: Database):
    await db.session.execute(text("TRUNCATE TABLE schedule CASCADE"))
    await db.session.execute(text("ALTER SEQUENCE subscriptions_id_seq RESTART WITH 1"))
    await db.session.execute(text("ALTER SEQUENCE schedule_id_seq RESTART WITH 1"))
    await db.session.execute(
        text("ALTER SEQUENCE schedule_position_seq RESTART WITH 1")
    )
    await db.session.commit()


async def parse_plan(db: Database):
    df = pd.read_csv(path_to_plan.absolute())
    df["next_code"] = df["code"].shift(-1)
    df.replace({np.nan: None}, inplace=True)
    participants_count = 0
    nominations_count = 0
    for index, row in df.iterrows():
        if row["code"] is not None:  # participant
            participant = await db.participant.get_by_where(
                Participant.title == row["voting_title"]
            )
            if participant:
                print(f"Участник {participant.title[0:40]}... уже существует")
                pass
            else:
                participant = await db.participant.new(
                    title=row["voting_title"], nomination_id=row["code"]
                )
                await db.session.flush([participant])
                print(f"Участник {row['voting_title'][0:40]}... добавлен в БД")
                participants_count += 1
            event = await db.event.new(participant_id=participant.id)
            await db.session.flush([event])
        elif row["code"] is None and row["next_code"] is not None:  # nomination
            nomination = await db.nomination.get_by_where(
                Nomination.id == row["next_code"]
            )
            if nomination:
                print(f"Номинация {row['info']} уже существует")
            else:
                print(f"Добавляем номинацию {row['info']}...")
                while True:
                    choice = input(
                        "Разрешить голосование за эту номинацию? Y - да, N - нет\n"
                    )
                    if choice.lower() == "y":
                        votable = True
                        break
                    elif choice.lower() == "n":
                        votable = False
                        break
                nomination = await db.nomination.new(
                    nomination_id=row["next_code"], title=row["info"], votable=votable
                )
                await db.session.flush([nomination])
                print(f"Номинация {row['info']} добавлена в БД")
                nominations_count += 1
        elif row["code"] is None and row["next_code"] is None:  # schedule entry
            event = await db.event.new(title=row["info"])
            await db.session.flush([event])
            print(f"Событие {row['info']} добавлено в БД")
    await db.session.commit()
    return participants_count, nominations_count


async def main(session_pool):
    async with session_pool() as session:
        db = Database(session)
        print("Очищаем расписание...")
        await clean_schedule(db)
        print("Расписание очищено! Переходим к парсингу плана...")
        participants_count, nominations_count = await parse_plan(db)
        events_count = await db.event.get_count(True)
        print(
            f"Парсинг завершён! Было добавлено {str(nominations_count)} новых номинаций, "
            f"{str(participants_count)} новых участников и {str(events_count)} событий."
        )
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
