import html

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import QuoteORM
from fanfan.application.common.id_provider import IdProvider


class GetRandomQuote:
    def __init__(self, session: AsyncSession, id_provider: IdProvider) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(self) -> str | None:
        query = select(QuoteORM.text).order_by(func.random()).limit(1)
        quote = await self.session.scalar(query)

        # Personalize quote
        if quote:
            user = await self.id_provider.get_current_user()
            replacements = {
                "%username%": user.username,
                "%first_name%": html.escape(user.first_name)
                if user.first_name
                else None,
                "%last_name%": html.escape(user.last_name) if user.last_name else None,
            }
            for placeholder, value in replacements.items():
                if value:
                    quote = quote.replace(placeholder, value)

        return quote
