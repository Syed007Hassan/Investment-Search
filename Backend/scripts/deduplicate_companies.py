"""
Utility to find and remove duplicate companies (same name + location), keeping the earliest (smallest id).
Prints actions to console.
"""

import sys
import logging
from sqlalchemy import text

sys.path.append(".")

from models.database import get_db_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def deduplicate():
    with get_db_session() as session:
        logger.info("[dedupe] scanning for duplicates by (name, location)…")
        rows = session.execute(text(
            """
            SELECT name, location, array_agg(id ORDER BY id) AS ids,
                   COUNT(*) as cnt
            FROM "Company"
            GROUP BY name, location
            HAVING COUNT(*) > 1
            """
        )).fetchall()
        if not rows:
            logger.info("[dedupe] no duplicates found.")
            return

        total_removed = 0
        for name, location, ids, cnt in rows:
            keep_id = ids[0]
            remove_ids = ids[1:]
            logger.info("[dedupe] %s (%s): keep id=%s remove ids=%s", name, location, keep_id, remove_ids)
            session.execute(text("DELETE FROM \"Company\" WHERE id = ANY(:ids)"), {"ids": remove_ids})
            total_removed += len(remove_ids)
        session.commit()
        logger.info("[dedupe] removed %d duplicate rows", total_removed)


if __name__ == "__main__":
    deduplicate()

