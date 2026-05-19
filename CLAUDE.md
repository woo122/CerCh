# 테크스캔 (TechScan) 프로젝트

## 프로젝트 개요
사람인 채용공고를 크롤링해서 기업이 요구하는 기술스택과 자격증을 AI로 추출하고, 이를 차트/순위로 시각화해주는 분석 웹사이트. 커뮤니티 기능도 포함.

## 기술 스택
- **Frontend**: HTML / CSS / JavaScript (순수 JS, 프레임워크 없음)
- **Backend**: Python FastAPI
- **Database**: SQLite
- **크롤링**: Python requests + BeautifulSoup (사람인 IT 직군)
- **AI 추출**: OpenAI API (채용공고 텍스트에서 기술스택/자격증 추출)
- **배포**: 미정 (포트폴리오용)

## 파일 구조
```
techscan/
│
├── frontend/
│   ├── index.html                 # 메인 페이지 (분석 탭 활성)
│   ├── pages/
│   │   ├── analysis.html          # 기술/자격증 분석 상세
│   │   ├── community.html         # 커뮤니티 글 목록
│   │   ├── community_post.html    # 커뮤니티 게시글 상세
│   │   ├── schedule.html          # 시험 일정
│   │   ├── mypage.html            # 마이페이지
│   │   ├── login.html             # 로그인
│   │   └── register.html          # 회원가입
│   ├── css/
│   │   └── common.css             # 공통 스타일 (헤더, 메뉴바, 푸터 등)
│   └── js/
│       ├── common.js              # 공통 함수 (헤더 렌더링 등)
│       └── api.js                 # FastAPI 백엔드 호출 함수 모음
│
├── backend/
│   ├── main.py                    # FastAPI 앱 진입점
│   ├── crawler/
│   │   └── techscan_crawler.py    # 사람인 크롤러 + OpenAI 기술/자격증 추출 + SQLite 저장
│   ├── api/
│   │   ├── auth.py                # 로그인 / 회원가입 API
│   │   ├── analysis.py            # 기술스택/자격증 데이터 API
│   │   └── community.py           # 커뮤니티 CRUD API
│   ├── models/
│   │   └── database.py            # DB 연결 및 모델 정의
│   └── requirements.txt           # Python 패키지 목록
│
└── database/
    └── techscan.db                # SQLite DB (크롤러 실행 시 자동 생성)
```

## 주요 기능
- 사람인 IT 직군 채용공고 크롤링 (BeautifulSoup)
- OpenAI API로 공고 텍스트에서 기술스택/자격증 자동 추출
- 기술 TOP 7 바 차트 시각화
- 인기 자격증 순위표
- 다가오는 시험 D-day 카운트다운
- 커뮤니티 (글쓰기 / 댓글 / 인기글)
- 회원가입 / 로그인 (이메일 + 비밀번호 + 닉네임, bcrypt 해싱)

## 회원 시스템
- 최소 구성: 이메일, 비밀번호(bcrypt), 닉네임
- 이메일 인증 없음 (포트폴리오용)
- 구직자/기업 역할 구분 없음

## 크롤러 구조 요약
1. 사람인 IT 직군 페이지 순회
2. 공고 10개씩 묶어서 OpenAI API로 기술스택/자격증 추출
3. SQLite(techscan.db)에 저장 (중복 URL 자동 무시)

## API 엔드포인트 (예정)
- `GET /api/techs` → 기술스택 순위 데이터
- `GET /api/certs` → 자격증 순위 데이터
- `POST /api/auth/register` → 회원가입
- `POST /api/auth/login` → 로그인
- `GET /api/community` → 커뮤니티 글 목록
- `POST /api/community` → 글 작성
