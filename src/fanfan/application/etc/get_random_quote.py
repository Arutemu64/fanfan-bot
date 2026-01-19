import html
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import QuoteORM
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider


class GetRandomQuote:
    def __init__(
        self, session: AsyncSession, id_provider: IdProvider, uow: UnitOfWork
    ) -> None:
        self.session = session
        self.id_provider = id_provider
        self.uow = uow

    async def __call__(self) -> str | None:
        quotes = (await self.session.scalars(select(QuoteORM))).all()
        if not quotes:
            return None

        weights = [1 / (q.view_count + 1) for q in quotes]
        quote_obj: QuoteORM = random.choices(quotes, weights=weights, k=1)[0]  # noqa: S311

        async with self.uow:
            quote_obj.view_count += 1
            await self.uow.commit()

        # Personalize quote
        quote_text = quote_obj.text
        user = await self.id_provider.get_current_user()
        replacements = {
            "%username%": user.username,
            "%first_name%": html.escape(user.first_name) if user.first_name else None,
            "%last_name%": html.escape(user.last_name) if user.last_name else None,
        }
        for placeholder, value in replacements.items():
            if value:
                quote_text = quote_text.replace(placeholder, value)

        return quote_text
