"""
서치 - 사람인/잡코리아 IT 직군 채용공고 크롤러
실행: python crawler.py
환경변수 OPENAI_API_KEY 필요
"""

import os       # 환경변수(OPENAI_API_KEY) 읽기
import re       # 공백 정규화, 코드블록 제거에 사용
import time     # 요청 간 딜레이(sleep)
import json     # techs/certs 리스트를 JSON 문자열로 DB 저장
import random   # 2~5초 랜덤 딜레이 생성
import sqlite3  # SQLite DB 연결 및 쿼리
from datetime import datetime  # (예비) 날짜 처리용
from pathlib import Path       # DB 파일 경로를 OS 독립적으로 구성

import requests                    # HTTP GET 요청 (사람인/잡코리아 페이지 다운로드)
from bs4 import BeautifulSoup      # HTML 파싱 및 CSS 셀렉터로 요소 추출
from openai import OpenAI          # gpt-4o-mini 호출로 기술스택/자격증 추출

# DB 파일 위치: 프로젝트 루트/database/search.db
DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "search.db"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")  # 환경변수에서 API 키 로드
MAX_PAGES = 10   # 사이트별 최대 수집 페이지 수
BATCH_SIZE = 10  # OpenAI 한 번 호출에 처리할 공고 수 (비용 절감)

# 브라우저로 위장하는 요청 헤더 (크롤링 차단 우회)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
}

client = OpenAI(api_key=OPENAI_API_KEY)  # OpenAI 클라이언트 초기화


# ── DB ────────────────────────────────────────────────────────────────────────

def init_db() -> sqlite3.Connection:
    """DB 파일과 jobs 테이블 생성 (없을 때만). 연결 객체 반환"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # database/ 폴더 없으면 생성
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            url        TEXT    UNIQUE NOT NULL,  -- 중복 방지 기준 키
            company    TEXT,
            title      TEXT,
            techs      TEXT,                     -- JSON 배열 문자열: ["Python", "Docker"]
            certs      TEXT,                     -- JSON 배열 문자열: ["정보처리기사"]
            crawled_at TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    return conn


def save_job(conn: sqlite3.Connection, url: str, company: str, title: str,
             techs: list[str], certs: list[str]) -> bool:
    """공고 1건을 DB에 저장. 중복 URL은 INSERT OR IGNORE로 무시.
    저장 성공 시 True, 중복이면 False 반환"""
    cur = conn.execute(
        "INSERT OR IGNORE INTO jobs (url, company, title, techs, certs) VALUES (?, ?, ?, ?, ?)",
        (url, company, title,
         json.dumps(techs, ensure_ascii=False),   # 리스트 → JSON 문자열 변환
         json.dumps(certs, ensure_ascii=False)),
    )
    conn.commit()
    return cur.lastrowid != 0  # lastrowid가 0이면 중복으로 무시된 것


# ── 사람인 크롤링 ──────────────────────────────────────────────────────────────

def saramin_urls(keyword: str = "개발자", pages: int = MAX_PAGES) -> list[dict]:
    """사람인 검색 결과 페이지를 순회하며 공고 URL/제목/회사명 수집"""
    results = []
    base = "https://www.saramin.co.kr/zf_user/search/recruit"
    for page in range(1, pages + 1):
        try:
            res = requests.get(
                base,
                params={
                    "searchword": keyword,  # 검색 키워드
                    "cat_mcls": "2",        # IT 직군 필터
                    "recruitPage": page,    # 페이지 번호
                },
                headers=HEADERS,
                timeout=10,
            )
            soup = BeautifulSoup(res.text, "html.parser")
            for item in soup.select(".item_recruit"):          # 공고 카드 각각
                a = item.select_one(".job_tit a")              # 공고 제목 링크
                company_el = item.select_one(".corp_name a")   # 회사명
                if not a:
                    continue
                href = a.get("href", "")
                results.append({
                    "url": "https://www.saramin.co.kr" + href if href.startswith("/") else href,
                    "title": a.get_text(strip=True),
                    "company": company_el.get_text(strip=True) if company_el else "",
                    "source": "saramin",
                })
            print(f"  [사람인] {page}/{pages} 페이지 → 누적 {len(results)}건")
            time.sleep(random.uniform(2, 5))  # 서버 부하 방지용 랜덤 딜레이
        except Exception as e:
            print(f"  [사람인] {page}페이지 오류: {e}")
    return results


# ── 잡코리아 크롤링 ────────────────────────────────────────────────────────────

def jobkorea_urls(keyword: str = "개발자", pages: int = MAX_PAGES) -> list[dict]:
    """잡코리아 검색 결과 페이지를 순회하며 공고 URL/제목/회사명 수집"""
    results = []
    base = "https://www.jobkorea.co.kr/Search/"
    for page in range(1, pages + 1):
        try:
            res = requests.get(
                base,
                params={
                    "stext": keyword,        # 검색 키워드
                    "tabType": "recruit",    # 채용공고 탭
                    "Page_No": page,         # 페이지 번호
                },
                headers=HEADERS,
                timeout=10,
            )
            soup = BeautifulSoup(res.text, "html.parser")
            for item in soup.select(".list-post .post-list-info"):  # 공고 카드 각각
                a = item.select_one(".title a")     # 공고 제목 링크
                company_el = item.select_one(".name")  # 회사명
                if not a:
                    continue
                href = a.get("href", "")
                results.append({
                    "url": "https://www.jobkorea.co.kr" + href if href.startswith("/") else href,
                    "title": a.get_text(strip=True),
                    "company": company_el.get_text(strip=True) if company_el else "",
                    "source": "jobkorea",
                })
            print(f"  [잡코리아] {page}/{pages} 페이지 → 누적 {len(results)}건")
            time.sleep(random.uniform(2, 5))  # 서버 부하 방지용 랜덤 딜레이
        except Exception as e:
            print(f"  [잡코리아] {page}페이지 오류: {e}")
    return results


# ── 공고 본문 크롤링 ───────────────────────────────────────────────────────────

def fetch_body(url: str) -> str:
    """공고 상세 페이지 접속 후 본문 텍스트 추출 (최대 3000자).
    사람인/잡코리아 각각 다른 셀렉터를 순서대로 시도"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # 사람인 본문 영역 셀렉터 (우선 시도)
        body = soup.select_one(".jv_cont") or soup.select_one(".wrap_jv_cont")
        # 잡코리아 본문 영역 셀렉터 (사람인 셀렉터 실패 시 시도)
        if not body:
            body = soup.select_one(".recruit-info") or soup.select_one("#giContents")
        if not body:
            body = soup.body  # 어떤 셀렉터도 안 맞으면 전체 body 사용

        text = body.get_text(separator=" ", strip=True) if body else ""
        return re.sub(r"\s{2,}", " ", text)[:3000]  # 연속 공백 제거 후 3000자 제한
    except Exception:
        return ""  # 접속 실패 시 빈 문자열 반환 (크롤링 중단 방지)


# ── OpenAI 배치 추출 ───────────────────────────────────────────────────────────

# gpt-4o-mini에게 전달하는 시스템 프롬프트: JSON만 출력하도록 지시
EXTRACT_PROMPT = """다음 채용공고들에서 요구하는 기술스택과 자격증을 추출하세요.
JSON 배열만 출력하세요 (설명 없이):
[
  {
    "index": 공고번호(1부터),
    "techs": ["Python", "Docker", ...],
    "certs": ["정보처리기사", "SQLD", ...]
  },
  ...
]
기술스택: 프로그래밍 언어, 프레임워크, DB, 클라우드, 도구 등
자격증: 국가기술자격, 민간자격, 어학 자격 등 (없으면 빈 배열)"""


def extract_batch(postings: list[dict]) -> list[dict]:
    """공고 최대 10개를 하나의 프롬프트로 묶어 OpenAI에 전송.
    API 호출 횟수를 줄여 비용 절감"""
    # 각 공고를 [공고 N] 형식으로 이어붙여 하나의 텍스트 생성
    texts = "\n\n".join(
        f"[공고 {i+1}] 회사: {p['company']} / 제목: {p['title']}\n{p['body'][:400]}"
        for i, p in enumerate(postings)
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": EXTRACT_PROMPT},  # 출력 형식 지시
                {"role": "user", "content": texts},              # 실제 공고 텍스트
            ],
            temperature=0,      # 출력 일관성 최대화 (랜덤성 없음)
            max_tokens=2048,    # 응답 길이 제한
        )
        content = resp.choices[0].message.content.strip()
        # GPT가 ```json ... ``` 코드블록으로 감싸서 응답할 경우 제거
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        return json.loads(content)  # JSON 문자열 → 파이썬 리스트 변환
    except Exception as e:
        print(f"  [OpenAI] 추출 오류: {e}")
        return []  # 오류 시 빈 리스트 반환 (해당 배치 건너뜀)


# ── 메인 ──────────────────────────────────────────────────────────────────────

def run():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

    print("=== 서치 크롤러 시작 ===")
    conn = init_db()  # DB 연결 및 테이블 초기화

    # [1단계] 사람인 + 잡코리아 목록 페이지에서 URL만 빠르게 수집
    print("\n[1단계] 공고 URL 수집...")
    all_postings = []
    all_postings.extend(saramin_urls("개발자", MAX_PAGES))
    all_postings.extend(jobkorea_urls("개발자", MAX_PAGES))
    print(f"→ 총 {len(all_postings)}건 수집 완료\n")

    # [2단계] DB에 이미 저장된 URL 제외 (재실행 시 중복 작업 방지)
    existing = {
        row[0] for row in conn.execute("SELECT url FROM jobs").fetchall()
    }
    new_postings = [p for p in all_postings if p["url"] not in existing]
    print(f"[2단계] 신규 공고 {len(new_postings)}건 (중복 {len(all_postings)-len(new_postings)}건 제외)\n")

    # [3단계] 공고 상세 페이지 접속 → 본문 수집 → 10개씩 OpenAI 추출 → DB 저장
    print("[3단계] 본문 크롤링 + 기술스택/자격증 추출...")
    batch: list[dict] = []  # 10개씩 쌓을 임시 버퍼
    saved = 0               # 실제 저장된 건수 카운터

    for i, posting in enumerate(new_postings, 1):
        body = fetch_body(posting["url"])  # 상세 페이지 본문 크롤링
        posting["body"] = body
        batch.append(posting)
        print(f"  ({i}/{len(new_postings)}) {posting['company']} - {posting['title'][:40]}")

        # 배치가 10개 찼거나 마지막 공고일 때 OpenAI 호출
        if len(batch) >= BATCH_SIZE or i == len(new_postings):
            print(f"  → OpenAI 추출 ({len(batch)}개 묶음)...")
            results = extract_batch(batch)  # 기술스택/자격증 추출

            for r in results:
                idx = r.get("index", 0) - 1  # OpenAI가 반환한 1-based index → 0-based 변환
                if 0 <= idx < len(batch):
                    p = batch[idx]
                    ok = save_job(conn, p["url"], p["company"], p["title"],
                                  r.get("techs", []), r.get("certs", []))
                    if ok:
                        saved += 1

            batch = []  # 배치 버퍼 초기화
            time.sleep(random.uniform(2, 5))  # 다음 배치 전 딜레이

    conn.close()
    print(f"\n=== 완료: {saved}건 저장 ===")


if __name__ == "__main__":
    run()
