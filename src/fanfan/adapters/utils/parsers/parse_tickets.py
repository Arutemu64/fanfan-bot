import logging
from typing import BinaryIO

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import TicketORM
from fanfan.core.vo.user import UserRole

logger = logging.getLogger(__name__)


async def parse_tickets(file: BinaryIO, session: AsyncSession) -> None:
    tickets_df = pd.read_excel(
        file,
        converters={
            "id": str,
            "role": UserRole,
        },
    )
    for _index, row in tickets_df.iterrows():
        try:
            async with session.begin_nested():
                session.add(TicketORM(id=row["id"], role=row["role"]))
            logger.info("Parsed ticket %s with role %s", row["id"], row["role"])
        except IntegrityError:
            ticket = await session.get(TicketORM, row["id"])
            if not ticket:
                raise
            logger.info("Ticket %s already exist", row["id"])
    await session.commit()
