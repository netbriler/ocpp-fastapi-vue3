from sqlalchemy import text

from core.database import get_contextual_session


async def get_counters(account_id: str):
    async with get_contextual_session() as session:
        query = "SELECT " \
                "(SELECT COUNT(id) FROM locations " \
                "WHERE is_active = 't' AND account_id = '{account_id}') AS locations," \
                "(SELECT COUNT(cp.id) FROM charge_points cp " \
                "JOIN locations l ON l.id = cp.location_id " \
                "WHERE cp.is_active = 't' AND l.account_id = '{account_id}') as stations;" \
            .format(account_id=account_id)
        result = await session.execute(text(query))
        return result.fetchone()
