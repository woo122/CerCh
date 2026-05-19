"""
사람인 IT 직군 채용공고 크롤러
- 공고 10개씩 OpenAI API로 기술스택/자격증 추출
- techscan.db에 저장 (중복 URL 자동 무시)
실행: python techscan_crawler.py
"""

import time
import json
import sqlite3
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "techscan.db"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # .env로 관리 권장
SARAMIN_BASE = "https://www.saramin.co.kr/zf_user/jobs/list/job-category"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

CATEGORY_MAP = {
    "dev": "84",       # 개발·데이터
    "data": "86",      # 데이터분석
    "security": "88",  # 보안
    "cloud": "87",     # 클라우드
}

client = OpenAI(api_key=OPENAI_API_KEY)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_posting_urls(category_code: str, pages: int = 3) -> list[str]:
    urls = []
    for page in range(1, pages + 1):
        res = requests.get(
            SARAMIN_BASE,
            params={"cat_kewd": category_code, "page": page, "loc_mcd": "101000"},
            headers=HEADERS,
            timeout=10,
        )
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.select(".item_recruit .job_tit a"):
            href = a.get("href", "")
            if href:
                urls.append("https://www.saramin.co.kr" + href)
        time.sleep(1)
    return urls


def fetch_posting_text(url: str) -> tuple[str, str, str]:
    """Returns (title, company, raw_text)"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.select_one(".tit_job")
        company = soup.select_one(".corp_name a")
        body = soup.select_one(".jv_cont")
        return (
            title.get_text(strip=True) if title else "",
            company.get_text(strip=True) if company else "",
            body.get_text(separator=" ", strip=True)[:3000] if body else "",
        )
    except Exception:
        return "", "", ""


def extract_with_openai(postings: list[dict]) -> list[dict]:
    texts = "\n\n".join(
        f"[공고 {i+1}] 제목: {p['title']}\n내용: {p['text'][:500]}"
        for i, p in enumerate(postings)
    )
    prompt = f"""다음 채용공고들에서 요구하는 기술스택과 자격증을 추출해주세요.
JSON 배열 형식으로 응답하세요. 각 항목은 아래 구조를 따르세요:
[
  {{
    "index": 공고번호(1부터),
    "techs": [{{"name": "기술명", "category": "dev|data|security|cloud"}}],
    "certs": ["자격증명"]
  }}
]
기술스택 예: Python, Java, Docker, Kubernetes, AWS, SQL, React 등
자격증 예: 정보처리기사, SQLD, AWS SAA, 리눅스마스터 등
응답은 JSON만 출력하세요.

채용공고:
{texts}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content)


def save_to_db(url: str, title: str, company: str, raw_text: str, techs: list, certs: list):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT OR IGNORE INTO job_postings (url, title, company, raw_text) VALUES (?, ?, ?, ?)",
            (url, title, company, raw_text),
        )
        conn.commit()
        if cur.lastrowid == 0:
            conn.close()
            return  # 중복 URL
        posting_id = cur.lastrowid
        for tech in techs:
            conn.execute(
                "INSERT INTO tech_mentions (posting_id, tech_name, category) VALUES (?, ?, ?)",
                (posting_id, tech["name"], tech.get("category", "")),
            )
        for cert in certs:
            conn.execute(
                "INSERT INTO cert_mentions (posting_id, cert_name) VALUES (?, ?)",
                (posting_id, cert),
            )
        conn.commit()
    finally:
        conn.close()


def run(pages_per_category: int = 3):
    for category, code in CATEGORY_MAP.items():
        print(f"[크롤링] {category} 카테고리...")
        urls = fetch_posting_urls(code, pages=pages_per_category)
        print(f"  → {len(urls)}개 URL 수집")

        batch = []
        for url in urls:
            title, company, text = fetch_posting_text(url)
            if text:
                batch.append({"url": url, "title": title, "company": company, "text": text})
            time.sleep(0.5)

            if len(batch) >= 10:
                print(f"  → OpenAI 추출 중 ({len(batch)}개)...")
                results = extract_with_openai(batch)
                for r in results:
                    idx = r["index"] - 1
                    if 0 <= idx < len(batch):
                        p = batch[idx]
                        save_to_db(p["url"], p["title"], p["company"], p["text"], r.get("techs", []), r.get("certs", []))
                batch = []
                time.sleep(2)

        if batch:
            print(f"  → OpenAI 추출 중 ({len(batch)}개)...")
            results = extract_with_openai(batch)
            for r in results:
                idx = r["index"] - 1
                if 0 <= idx < len(batch):
                    p = batch[idx]
                    save_to_db(p["url"], p["title"], p["company"], p["text"], r.get("techs", []), r.get("certs", []))

    print("크롤링 완료!")


if __name__ == "__main__":
    run()
