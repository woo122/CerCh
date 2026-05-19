from fastapi import APIRouter, Query
from models.database import get_conn

router = APIRouter()

CATEGORY_MAP = {
    "개발": "dev",
    "데이터": "data",
    "보안": "security",
    "클라우드": "cloud",
}


@router.get("/techs")
def get_techs(filter: str = Query(default="", description="직군 필터 (개발/데이터/보안/클라우드)")):
    conn = get_conn()
    if filter and filter in CATEGORY_MAP:
        rows = conn.execute(
            """
            SELECT tech_name, COUNT(*) as count
            FROM tech_mentions
            WHERE category = ?
            GROUP BY tech_name
            ORDER BY count DESC
            LIMIT 7
            """,
            (CATEGORY_MAP[filter],),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT tech_name, COUNT(*) as count
            FROM tech_mentions
            GROUP BY tech_name
            ORDER BY count DESC
            LIMIT 7
            """
        ).fetchall()
    conn.close()
    total = sum(r["count"] for r in rows) or 1
    return [
        {"rank": i + 1, "name": r["tech_name"], "count": r["count"], "ratio": round(r["count"] / total * 100, 1)}
        for i, r in enumerate(rows)
    ]


@router.get("/certs")
def get_certs():
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT cert_name, COUNT(*) as count
        FROM cert_mentions
        GROUP BY cert_name
        ORDER BY count DESC
        LIMIT 10
        """
    ).fetchall()
    conn.close()
    return [{"rank": i + 1, "name": r["cert_name"], "count": r["count"]} for i, r in enumerate(rows)]


@router.get("/stats")
def get_stats():
    conn = get_conn()
    total_postings = conn.execute("SELECT COUNT(*) as c FROM job_postings").fetchone()["c"]
    total_techs = conn.execute("SELECT COUNT(DISTINCT tech_name) as c FROM tech_mentions").fetchone()["c"]
    total_certs = conn.execute("SELECT COUNT(DISTINCT cert_name) as c FROM cert_mentions").fetchone()["c"]
    conn.close()
    return {"total_postings": total_postings, "total_techs": total_techs, "total_certs": total_certs}
